using System.Text;
using Azure;
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
IKernelMemory? memory = null;

using var loggerFactory = LoggerFactory.Create(builder =>
{
    builder
        .AddConsole()
        .AddDebug()
        .SetMinimumLevel(LogLevel.Debug);
});

var logger = loggerFactory.CreateLogger<Program>();

async void initialize()
{
    var logLevel = LogLevel.Warning;
    SensitiveDataLogger.Enabled = false;

    var config = new OllamaConfig
    {
        Endpoint = "http://localhost:11434",
        TextModel = new OllamaModelConfig("llama2:7b"),
        EmbeddingModel = new OllamaModelConfig("mxbai-embed-large:latest")
    };

    memory = new KernelMemoryBuilder()
        .WithOllamaTextGeneration(config, new GPT4oTokenizer())
        .WithOllamaTextEmbeddingGeneration(config, new GPT4oTokenizer())
        .Configure(builder => builder.Services
            .AddLogging(l =>
            {
                l.SetMinimumLevel(logLevel);
                l.AddSimpleConsole(c => c.SingleLine = true);
            }))
        .Build();

    await memory.ImportTextAsync("My name is Sunlless the actual goat!");

    var answer = await memory.AskAsync("What is my name?");
    logger.LogInformation(answer.Result);
}

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

    foreach (IFormFile file in files)
        try
        {
            if(memory == null)
                return Results.StatusCode(500);
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

//initialize();
app.Run();
