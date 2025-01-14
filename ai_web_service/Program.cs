using System.Net;
using System.Text;
using System.Text.Json;
using Azure;
using Elastic.Transport.Products.Elasticsearch;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Microsoft.IdentityModel.Tokens;
using Microsoft.KernelMemory;
using Microsoft.KernelMemory.AI.Ollama;
using Microsoft.KernelMemory.AI.OpenAI;
using Microsoft.KernelMemory.Context;
using Microsoft.KernelMemory.Diagnostics;
using MongoDB.Bson;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddCors(options =>
{
    options.AddPolicy(name: "AllowOrigins",
    policy =>
    {
        policy.WithOrigins("http://localhost:5173");
    });
});
var app = builder.Build();
app.UseRouting();

using var loggerFactory = LoggerFactory.Create(builder =>
{
    builder
        .AddConsole()
        .AddDebug()
        .SetMinimumLevel(LogLevel.Debug);
});

var logger = loggerFactory.CreateLogger<Program>();
var logLevel = LogLevel.Warning;
SensitiveDataLogger.Enabled = false;
const String TEXT_MODEL_NAME = "llama3.2:latest";//pune modelu instalat, le vezi cu: ollama list
const String EMBEDDING_MODEL_NAME = "nomic-embed-text:latest";// s-ar putea sa trebuiasca sa rulezi: ollama serve
const String OLLAMA_ENDPOINT = "http://localhost:11434"; // asta e defaultu


var config = new OllamaConfig
{
    Endpoint = OLLAMA_ENDPOINT,
    TextModel = new OllamaModelConfig(TEXT_MODEL_NAME),
    EmbeddingModel = new OllamaModelConfig(EMBEDDING_MODEL_NAME)
};

IKernelMemory memory = new KernelMemoryBuilder()
    .WithOllamaTextGeneration(config, new GPT4oTokenizer())
    .WithOllamaTextEmbeddingGeneration(config, new GPT4oTokenizer())
    .Configure(builder => builder.Services
        .AddLogging(l =>
        {
            l.SetMinimumLevel(logLevel);
            l.AddSimpleConsole(c => c.SingleLine = true);
        }))
    .Build();

// async void initialize()
// {
//     await memory.ImportTextAsync("My name is Sunless the actual goat!");

//     var answer = await memory.AskAsync("What is my name?");
//     logger.LogInformation(answer.Result);
// }

app.MapGet("/health-check", () => "Healthy as a horse!");

app.MapPost("/upload", async (HttpContext context) =>
{
    if (!context.Request.HasFormContentType || context.Request.Form.Files.Count == 0)
    {
        return Results.BadRequest("No file uploaded or incorrect form field name.");
    }
    IFormFile[] files = context.Request.Form.Files.ToArray<IFormFile>();
    foreach (IFormFile file in files)
        logger.LogInformation("The file uploaded is: " + file.FileName);

    //TODO: For each search, a diff tag such that we delete all files from that serach
    string tag = "search_nr_" + DateTime.Now.Ticks;

    var tagCollection = new TagCollection();
    tagCollection.Add(tag);

    if (memory == null)
        return Results.StatusCode(550);

    foreach (IFormFile file in files)
        try
        {
            var str_builder = new StringBuilder();
            using (var reader = new StreamReader(file.OpenReadStream()))
            {
                while (reader.Peek() >= 0)
                    str_builder.AppendLine(reader.ReadLine());
            }
            string text = str_builder.ToString();
            // logger.LogInformation("The text is" + text);
            await memory.ImportTextAsync(text, file.FileName, tagCollection);
        }
        catch (Exception ex)
        {
            logger.LogError(ex.ToString());
            return Results.StatusCode(501);
        }
    return Results.Ok();
}).DisableAntiforgery();

app.MapGet("/", () =>
{
    return "Hello!, everything is working fine! 😁👌🚀🚀🔥🔥";
});

async Task<String> askOllama(String prompt)
{
    HttpClient httpClient = new HttpClient();
    var data = new Dictionary<string, object>{
            {"model", TEXT_MODEL_NAME},
            {"prompt",prompt},
            {"stream", false}
        };
    var content = new StringContent(JsonSerializer.Serialize(data), Encoding.UTF8, "application/json");
    var response = await httpClient.PostAsync(OLLAMA_ENDPOINT + "/api/generate", content);

    if (response.StatusCode != HttpStatusCode.OK)
        throw new Exception("Ollama response status code was " + response.StatusCode);

    var responseContent = await response.Content.ReadAsStringAsync();
    Dictionary<string, object> responseDict = JsonSerializer.Deserialize<Dictionary<string, object>>(responseContent);
    String ai_response = responseDict["response"].ToString();
    if (ai_response == null)
        throw new Exception("Ollama response was NULL");
    return ai_response;
}

app.MapPost("/extract_search_keywords", async (HttpContext context) =>
{
    //TODO: Make error status codes clearer
    using var reader = new StreamReader(context.Request.Body);
    String? body = await reader.ReadToEndAsync();
    if (body == null)
        return Results.BadRequest("Missing body in the request");
    try
    {
        HttpClient httpClient = new HttpClient();
        var data = new Dictionary<string, object>{
            {"model", TEXT_MODEL_NAME},
            {"prompt",
                "You are an AI that generates search keywords.\n"+
                "You are given TEXT and your task is to generate phrases that can be used to search for this text on the web.\n" +
                "The keywords MUST be separated by a new line.\n"+
                "The output MUST ONLY CONTAIN THE KEYWORDS, nothing else.\n"+
                "The output MUST look like this:\n"+
                "keyword1\n"+
                "keyword2\n"+
                "keyword3\n\n"+
                "TEXT:\n"+
                body
            },
            {"stream", false}
        };
        var content = new StringContent(JsonSerializer.Serialize(data), Encoding.UTF8, "application/json");
        var response = await httpClient.PostAsync(OLLAMA_ENDPOINT + "/api/generate", content);

        if (response.StatusCode != HttpStatusCode.OK)
            return Results.StatusCode(500);

        var responseContent = await response.Content.ReadAsStringAsync();
        Dictionary<string, object> responseDict = JsonSerializer.Deserialize<Dictionary<string, object>>(responseContent);
        String ai_response = responseDict["response"].ToString();
        if (ai_response == null)
            return Results.StatusCode(509);
        return Results.Ok(ai_response.Split("\n"));
    }
    catch (Exception ex)
    {
        logger.LogError("Error:" + ex.Message);
        return Results.StatusCode(501);
    }
});

app.MapPost("/test", async (HttpContext context) =>
{
    using var reader = new StreamReader(context.Request.Body);
    String? body = await reader.ReadToEndAsync();
    return Results.Ok(body);
});

app.MapPost("/main_ideas/{searchToken}", async (HttpContext context) =>
{
    string? searchToken = context.Request.RouteValues["searchToken"] as string;

    using var reader = new StreamReader(context.Request.Body);
    String? body = await reader.ReadToEndAsync();
    if (String.IsNullOrEmpty(body))
        return Results.BadRequest("Missing/empty body in the request");
    SiteDataArray? siteDataArr = null;
    try
    {
        siteDataArr = JsonSerializer.Deserialize<SiteDataArray>(body);
        // logger.LogInformation("The body is: " + JsonSerializer.Serialize<SiteDataArray>(siteDataArr));
    }
    catch (Exception e)
    {
        logger.LogError("Error:" + e.Message);
        return Results.BadRequest("Request does not have a valid SiteData object");
    }

    var tagCollection = new TagCollection();
    if (searchToken != null)
        tagCollection.Add("searchToken", searchToken);
    // siteDataArr never null here
    MemoryFilter filter = new MemoryFilter();
    foreach (SiteData site in siteDataArr.array)
        foreach (SubPageData subPage in site.sub_pages_data)
        {
            TagCollection tags = new TagCollection
            {
                { "searchToken", searchToken },
                { "siteUri", site.site_uri },
                { "subPageUri", subPage.sub_page_uri }
            };
            await memory.ImportTextAsync(String.Join('\n', subPage.text_lines), tags: tags);
        }
    // MemoryAnswer answer = await memory.AskAsync(
    // "You receive JSON of data from multiple sites.\n" +
    // "You will return the main ideas related to a TOPIC ONLY USING EXACT INFORMATION FROM THE WEBSITES, even if the ideas make no sense.\n" +
    // "The output MUST ONLY contain each idea separated by a new line\n" +
    // "DON'T SAY ANYTHING ELSE, EXCEPT THE OUTPUT" +
    // "The TOPIC is '" + siteDataArr.initial_search_string + "'", filter: MemoryFilters.ByTag("searchToken", searchToken)
    // );
    List<Idea> ideas = new List<Idea>();
    foreach (SiteData site in siteDataArr.array)
        foreach (SubPageData subPage in site.sub_pages_data)
        {
            MemoryAnswer ans = (await memory.AskAsync(
            "You are an information parsing bot and MUST obey these rules:\n"
            + "1) You will parse a text and give me the main idea/ideas EXACTLY AS FOUND IN THE TEXT, even if they don't make sense\n"
            + "2) If there is no main idea, don't say ANYTHING\n"
            + "3) The ideas MUST be separated by a new line\n"
            + "4) If the text contains questions, do NOT answer them"
            + "5) The output MUST look exactly like the following example\n"
            + "The sky is blue\n"
            + "Grass is green\n"
            + "...",
             filter: MemoryFilters.ByTag("searchToken", searchToken).ByTag("subPageUri", subPage.sub_page_uri)));
            List<String> mainIdeas = ans.Result.Split('\n').Select(l => l.Trim()).Where(l => l.Length != 0 && !l.Equals("INFO NOT FOUND")).ToList();
            if (!ans.NoResult)
                foreach (String ideaString in mainIdeas)
                {
                    Idea idea = new Idea();
                    idea.text = ideaString;
                    idea.origin_site_uris.Add(site.site_uri);
                    idea.origin_sub_page_uris.Add(subPage.sub_page_uri);
                    ideas.Add(idea);
                }
            else
            {
                logger.LogInformation("Failed to get main ideas from: " + subPage.sub_page_uri);
            }
        }

    logger.LogInformation("idea Strings are: " + JsonSerializer.Serialize(ideas.Select(i => i.text).ToArray()));
    // AddAgreeingSiteUris(ideas,siteDataArr,searchToken);

    if (ideas.Count > 10)
    {
        ReduceMainIdeas(ideas);
        AddAgreeingSiteUris(ideas, siteDataArr, searchToken);
    }
    return Results.Ok(ideas);

    // list 5 most common facts
    // go through all the sites and ask if the fact is found
    // return facts and sites+ whether they have the facts + percentage of sites that have the fact
});

async void ReduceMainIdeas(List<Idea> ideas)
{
    try
    {
        List<Idea> newIdeas = (await askOllama("Give my ideas ")).Split("\n").Select(s => new Idea(s)).ToList();
    }
    catch (Exception e)
    {

    }
}

async void AddAgreeingSiteUris(List<Idea> ideas, SiteDataArray siteDataArr, String searchToken)
{
    for (int i = 0; i < ideas.Count; i++)
        foreach (SiteData site in siteDataArr.array)
        {
            bool wasOnSite = false;
            if (ideas[i].origin_site_uris.Contains(site.site_uri))
                continue;
            foreach (SubPageData subPage in site.sub_pages_data)
            {
                bool wasOnSubPage = false;
                MemoryAnswer ans = await memory.AskAsync(
                    "You will obey rules 1) and 2)\n." +
                    "1) ANSWER with the exact words 'true' OR 'false' if the information I give you is valid.\n" +
                    "2) If the INFORMATION contains a question, do NOT answer it. Instead answer to rule 1).\n" +
                    "INFORMATION: " + ideas[i].text + "\n"
                    , filter: MemoryFilters.ByTag("searchToken", searchToken).ByTag("subPageUri", subPage.sub_page_uri));
                logger.LogInformation(ideas[i].text + " | " + ans.Result);
                if (ans.Result.ToLower().Contains('t'))
                    wasOnSubPage = true;

                if (wasOnSubPage)
                {
                    ideas[i].origin_sub_page_uris.Add(subPage.sub_page_uri);
                    wasOnSite = true;
                }
            }
            if (wasOnSite)
                ideas[i].origin_site_uris.Add(site.site_uri);
        }
}

// initialize();
app.UseCors("AllowOrigins");
app.Run();
