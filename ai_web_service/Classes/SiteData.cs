using System.Text.Json.Serialization;
using ThirdParty.Json.LitJson;

public class SubPageData{
    [JsonPropertyName("sub_page_uri")]
    public String sub_page_uri {get; set;}

    [JsonPropertyName("text_lines")]
    public String[] text_lines {get; set;}
} 

class SiteData(){
    [JsonPropertyName("sub_pages_data")]
    public SubPageData[] sub_pages_data {get; set;}

    [JsonPropertyName("site_uri")]
    public String site_uri {get;set;}
}

class SiteDataArray(){
    [JsonPropertyName("array")]
    public SiteData[] array {get; set;}
}