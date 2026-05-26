namespace SmartSecurityIoT.Security;

public static class SecureConfig
{
    private static string GetOrThrow(string key) =>
        Environment.GetEnvironmentVariable(key)
        ?? throw new InvalidOperationException(
            $"Critical configuration missing: {key}. Please set this environment variable.");

    public static string TelegramToken =>
        GetOrThrow("TELEGRAM_BOT_TOKEN");

    public static string TelegramChatId =>
        GetOrThrow("TELEGRAM_CHAT_ID");

    public static string PlcIp =>
        GetOrThrow("PLC_IP");

    public static string RtspUrl =>
        GetOrThrow("RTSP_URL");

    public static string DatabasePassword =>
        GetOrThrow("DB_ENCRYPTION_KEY");
}
