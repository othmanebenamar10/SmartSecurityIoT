using System.Net.Http;
using System.Net.Http.Headers;
using Serilog;
using SmartSecurityIoT.Services.Interfaces;

namespace SmartSecurityIoT.Services;

public class NotificationService : INotificationService
{
    private readonly HttpClient _httpClient = new();
    private readonly string _botToken;
    private readonly ILogger _logger = Log.ForContext<NotificationService>();

    public NotificationService()
    {
        _botToken = Security.SecureConfig.TelegramToken;
    }

    public async Task SendTelegramAlertAsync(string message, string imagePath)
    {
        try
        {
            if (!string.IsNullOrEmpty(imagePath) && File.Exists(imagePath))
            {
                await SendPhotoAsync(message, imagePath);
            }
            else
            {
                await SendMessageAsync(message);
            }
        }
        catch (Exception ex)
        {
            _logger.Error(ex, "Failed to send Telegram alert: {Message}", message);
        }
    }

    private async Task SendMessageAsync(string text)
    {
        var url = $"https://api.telegram.org/bot{_botToken}/sendMessage";
        var chatId = Security.SecureConfig.TelegramChatId;

        var content = new FormUrlEncodedContent(new[]
        {
            new KeyValuePair<string, string>("chat_id", chatId),
            new KeyValuePair<string, string>("text", text),
            new KeyValuePair<string, string>("parse_mode", "HTML")
        });

        var response = await _httpClient.PostAsync(url, content);
        if (response.IsSuccessStatusCode)
        {
            _logger.Information("Telegram message sent: {Text}", text);
        }
        else
        {
            var body = await response.Content.ReadAsStringAsync();
            _logger.Warning("Telegram API error: {StatusCode} - {Body}",
                response.StatusCode, body);
        }
    }

    private async Task SendPhotoAsync(string caption, string imagePath)
    {
        var url = $"https://api.telegram.org/bot{_botToken}/sendPhoto";
        var chatId = Security.SecureConfig.TelegramChatId;

        using var form = new MultipartFormDataContent();
        form.Add(new StringContent(chatId), "chat_id");
        form.Add(new StringContent(caption), "caption");
        form.Add(new StringContent("HTML"), "parse_mode");

        var imageBytes = await File.ReadAllBytesAsync(imagePath);
        var imageContent = new ByteArrayContent(imageBytes);
        imageContent.Headers.ContentType = new MediaTypeHeaderValue("image/jpeg");
        form.Add(imageContent, "photo", Path.GetFileName(imagePath));

        var response = await _httpClient.PostAsync(url, form);
        if (response.IsSuccessStatusCode)
        {
            _logger.Information("Telegram photo sent: {Caption}", caption);
        }
        else
        {
            var body = await response.Content.ReadAsStringAsync();
            _logger.Warning("Telegram API error: {StatusCode} - {Body}",
                response.StatusCode, body);
        }
    }
}
