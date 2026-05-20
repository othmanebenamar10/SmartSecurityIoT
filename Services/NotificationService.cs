using System.Threading.Tasks;
using SmartSecurityIoT.Services.Interfaces;

namespace SmartSecurityIoT.Services
{
    public class NotificationService : INotificationService
    {
        public Task SendTelegramAlertAsync(string message, string imagePath) => Task.CompletedTask;
    }
}