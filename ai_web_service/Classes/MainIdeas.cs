using System.Text.Json.Serialization;


public class Idea
{
    [JsonPropertyName("text")]
    public String text { get; set; }

    [JsonPropertyName("origin_sub_page_uris")]
    public List<String> origin_sub_page_uris { get; set; }

    [JsonPropertyName("origin_site_uris")]
    public List<String> origin_site_uris { get; set; }

    public Idea()
    {
        origin_site_uris = new List<string>();
        origin_sub_page_uris = new List<string>();
    }
}

public class MainIdeas
{
    [JsonPropertyName("ideas")]
    public List<Idea> ideas { get; set; }

}