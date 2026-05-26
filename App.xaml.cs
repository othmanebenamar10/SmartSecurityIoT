using System.Windows;
using Microsoft.Extensions.DependencyInjection;
using SmartSecurityIoT.Services;
using SmartSecurityIoT.Services.Interfaces;
using SmartSecurityIoT.ViewModels;
using SmartSecurityIoT.Views;

namespace SmartSecurityIoT;

public partial class App : Application
{
    public IServiceProvider Services { get; }

    public App()
    {
        Services = ConfigureServices();
    }

    private static IServiceProvider ConfigureServices()
    {
        var services = new ServiceCollection();

        services.AddSingleton<IBiometricService, BiometricService>();
        services.AddSingleton<IPlcService, PlcService>();
        services.AddSingleton<INotificationService, NotificationService>();
        services.AddSingleton<IVideoService, VideoService>();

        services.AddTransient<MainViewModel>();

        return services.BuildServiceProvider();
    }

    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);
        var window = new MainWindow
        {
            DataContext = Services.GetRequiredService<MainViewModel>()
        };
        window.Show();
    }
}
