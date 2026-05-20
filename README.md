
# Smart Security IoT - .NET 8 WPF

Projet de contrôle d’accès résidentiel intelligent sécurisé.

## Stack Technique
- .NET 8
- WPF + MVVM
- OpenCvSharp / FaceRecognitionDotNet
- Sharp7
- SQLite + SQLCipher
- Telegram Bot API
- Material Design In XAML

## Packages NuGet recommandés
- CommunityToolkit.Mvvm
- MaterialDesignThemes
- MaterialDesignColors
- OpenCvSharp4
- OpenCvSharp4.runtime.win
- FaceRecognitionDotNet
- Sharp7
- Microsoft.Data.Sqlite
- SQLitePCLRaw.bundle_e_sqlcipher
- Dapper
- Serilog
- Serilog.Sinks.File

## Sécurité
- Aucun secret hardcodé
- Variables d’environnement / Windows Credential Manager
- Embeddings biométriques AES-256
- Seuil strict : 0.40
- Anti-spoofing via clignement des yeux
