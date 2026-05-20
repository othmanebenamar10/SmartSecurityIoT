<<<<<<< HEAD
using System.Threading.Tasks;

namespace SmartSecurityIoT.Services.Interfaces
{
    public interface INotificationService
    {
        Task SendAlertAsync(string message);
    }
}
=======

namespace SmartSecurityIoT.Services.Interfaces;

public interface INotificationService
{
    Task SendTelegramAlertAsync(string message, string imagePath);
}
>>>>>>> 1040ed1220214f4df9d7b4c004650f5c501a03e8
