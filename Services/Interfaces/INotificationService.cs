
namespace SmartSecurityIoT.Services.Interfaces;

public interface INotificationService
{
    Task SendTelegramAlertAsync(string message, string imagePath);
}
