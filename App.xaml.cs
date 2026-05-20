<<<<<<< HEAD
using System.Threading.Tasks;
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

        // Services
        services.AddSingleton<IBiometricService, BiometricService>();
        services.AddSingleton<IPlcService, PlcService>();
        services.AddSingleton<INotificationService, NotificationService>();
        services.AddSingleton<IVideoService, VideoService>();

        // ViewModels
        services.AddTransient<MainViewModel>();

        return services.BuildServiceProvider();
    }

    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);
        var window = new MainWindow { DataContext = ((App)Current).Services.GetService<MainViewModel>() };
        window.Show();
    }
=======
using System.Windows;

namespace SmartSecurityIoT;

public partial class App : Application
{
    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);

        MainWindow window = new MainWindow();

        window.Show();
    }
>>>>>>> 1040ed1220214f4df9d7b4c004650f5c501a03e8
}