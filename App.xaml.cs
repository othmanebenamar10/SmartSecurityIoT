using System.Windows;
using Microsoft.Extensions.DependencyInjection;
using Serilog;
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
        ConfigureLogging();
        Services = ConfigureServices();
    }

    private static void ConfigureLogging()
    {
        var logPath = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "SmartSecurityIoT",
            "logs",
            "app-.log");

        Log.Logger = new LoggerConfiguration()
            .MinimumLevel.Information()
            .WriteTo.File(logPath,
                rollingInterval: RollingInterval.Day,
                retainedFileCountLimit: 30,
                outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff} [{Level:u3}] {SourceContext} | {Message:lj}{NewLine}{Exception}")
            .CreateLogger();

        Log.Information("SmartSecurityIoT starting up");
    }

    private static IServiceProvider ConfigureServices()
    {
        var services = new ServiceCollection();

        services.AddSingleton<IDatabaseService, DatabaseService>();
        services.AddSingleton<IBiometricService, BiometricService>();
        services.AddSingleton<IPlcService, PlcService>();
        services.AddSingleton<INotificationService, NotificationService>();
        services.AddSingleton<IVideoService, VideoService>();

        services.AddTransient<MainViewModel>();

        return services.BuildServiceProvider();
    }

    protected override async void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);

        try
        {
            var dbService = Services.GetRequiredService<IDatabaseService>();
            await dbService.InitializeAsync();
        }
        catch (Exception ex)
        {
            Log.Error(ex, "Failed to initialize database");
        }

        var window = new MainWindow
        {
            DataContext = Services.GetRequiredService<MainViewModel>()
        };
        window.Show();
    }

    protected override void OnExit(ExitEventArgs e)
    {
        Log.Information("SmartSecurityIoT shutting down");
        Log.CloseAndFlush();
        base.OnExit(e);
    }
}
