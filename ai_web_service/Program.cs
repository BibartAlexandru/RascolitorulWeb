using System.Net;
using System.Text;
using System.Text.Json;
using Azure;
using Elastic.Transport.Products.Elasticsearch;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Microsoft.KernelMemory;
using Microsoft.KernelMemory.AI.Ollama;
using Microsoft.KernelMemory.AI.OpenAI;
using Microsoft.KernelMemory.Context;
using Microsoft.KernelMemory.Diagnostics;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
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
    foreach(IFormFile file in files)
        logger.LogInformation("The file uploaded is: " + file.FileName);

    //TODO: For each search, a diff tag such that we delete all files from that serach
    string tag = "search_nr_" + DateTime.Now.Ticks;
    
    var tagCollection = new TagCollection();
    tagCollection.Add(tag);

    if(memory == null)
        return Results.StatusCode(550);

    foreach (IFormFile file in files)
        try
        {
            var str_builder = new StringBuilder();
            using (var reader = new StreamReader(file.OpenReadStream())){
                while (reader.Peek() >= 0)
                    str_builder.AppendLine(reader.ReadLine());
            }
            string text = str_builder.ToString();
            // logger.LogInformation("The text is" + text);
            await memory.ImportTextAsync(text, file.FileName, tagCollection);
        }
        catch(Exception ex)
        {
            return Results.StatusCode(501);
        }
    return Results.Ok();
}).DisableAntiforgery();

app.MapGet("/", async () => {
    return "Hello!, everything is working fine! 😁👌🚀🚀🔥🔥";
});

app.MapPost("/extract_search_keywords", async (HttpContext context) => {
    //TODO: Make error status codes clearer
    using var reader = new StreamReader(context.Request.Body);
    String? body = await reader.ReadToEndAsync();
    if (body == null)
        return Results.BadRequest("Missing body in the request");
    try{
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

        if(response.StatusCode != HttpStatusCode.OK)
            return Results.StatusCode(500);

        var responseContent = await response.Content.ReadAsStringAsync();
        Dictionary<string,object> responseDict = JsonSerializer.Deserialize<Dictionary<string,object>>(responseContent);
        String ai_response = responseDict["response"].ToString();
        if(ai_response == null)
            return Results.StatusCode(509);
        return Results.Ok(ai_response.Split("\n"));
    }
    catch(Exception ex)
    {
        logger.LogError("Error:" + ex.Message);
        return Results.StatusCode(501);
    }
});

app.MapPost("/most_common_facts",async (HttpContext context) => {
    // receive crawled data
    // list 5 most common facts
    // go through all the sites and ask if the fact is found
    // return facts and sites+ whether they have the facts + percentage of sites that have the fact
});

// initialize();
app.Run();
