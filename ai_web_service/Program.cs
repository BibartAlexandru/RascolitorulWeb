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

    var memory = new KernelMemoryBuilder()
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
    Console.WriteLine(answer.Result);
}

app.MapGet("/health-check", () => "Healthy as a horse!");

app.MapPost("/upload", (HttpContext context) =>
{
    if (!context.Request.HasFormContentType || context.Request.Form.Files["file"] == null)
    {
        return Results.BadRequest("No file uploaded or incorrect form field name.");
    }
    IFormFile file = context.Request.Form.Files["file"];
    Console.WriteLine("The file uploaded is: " + file.FileName);
    return Results.Ok();
}).DisableAntiforgery();

app.MapGet("/", async () => {
    return "Hello!, everything is working fine! 😁👌🚀🚀🔥🔥";
});

//initialize();
app.Run();
