using SmartSecurityIoT.Services.Interfaces;

namespace SmartSecurityIoT.Services;

public class NotificationService : INotificationService
{
    public Task SendTelegramAlertAsync(string message, string imagePath)
    {
        // TODO: Implémenter l'envoi via Telegram Bot API
        return Task.CompletedTask;
    }
}
