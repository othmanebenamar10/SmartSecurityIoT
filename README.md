# 🏠 SmartSecurityHome IA : La Sentinelle Intelligente

<p align="center">
  <img src="https://img.icons8.com/fluency/120/home.png" width="120" alt="SmartSecurityHome Logo" />
</p>

<p align="center">
  <strong>Transformez votre maison en forteresse intelligente.</strong><br />
  <em>Une solution de contrôle d'accès résidentiel de pointe fusionnant l'Intelligence Artificielle Biométrique et la fiabilité des automates Siemens LOGO! V8.</em>
</p>

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/.NET-8.0-512bd4?style=for-the-badge&logo=dotnet" alt=".NET 8" /></a>
  <a href="#"><img src="https://img.shields.io/badge/UI-WPF_Glassmorphism-blue?style=for-the-badge" alt="WPF" /></a>
  <a href="#"><img src="https://img.shields.io/badge/IA-Reconnaissance_Faciale-green?style=for-the-badge&logo=opencv" alt="OpenCV" /></a>
  <a href="#"><img src="https://img.shields.io/badge/Hardware-Siemens_LOGO!-orange?style=for-the-badge&logo=siemens" alt="Siemens" /></a>
  <a href="#"><img src="https://img.shields.io/badge/Security-ISO_27001-red?style=for-the-badge" alt="Security" /></a>
</p>

---

## 👤 Auteur & Créateur
Ce projet a été entièrement conçu et réalisé par **Othmane BENAMAR**.

<p align="left">
  <a href="https://www.linkedin.com/in/benamarothmane/"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
  <a href="https://github.com/othmanebenamar10"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub" /></a>
</p>

---

## 📜 Sommaire
1. Vision du Projet
2. Scénarios Domotiques
3. Détails Algorithmiques IA
4. Fonctionnalités Détaillées
5. Architecture Système
6. Installation & Configuration
7. Guide Matériel (Siemens LOGO!)
8. Sécurité & Vie Privée
9. Roadmap

---

## 🌟 Vision du Projet

**SmartSecurityHome** n'est pas une simple application de surveillance. C'est un écosystème qui unifie le monde des algorithmes IA complexes et la domotique physique câblée. 

Là où les solutions "grand public" (Ring, Nest) dépendent du Cloud et de serveurs tiers, ce projet tourne **100% en local** sur votre machine Windows, garantissant une latence minimale pour l'ouverture de votre portail et une confidentialité absolue pour vos données biométriques.

---

## 🏠 Scénarios Domotiques

*   **L'Accueil Personnalisé** : Vous rentrez des courses les bras chargés. La caméra EZVIZ vous identifie à 3 mètres. Le Siemens LOGO! reçoit l'ordre de déverrouiller la gâche électrique et d'allumer le plafonnier de l'entrée.
*   **Le Mode "Nuit Vigilante"** : Entre 23h et 6h, toute détection de visage inconnu active un projecteur extérieur via l'automate et fait hurler une sirène intérieure, tout en vous envoyant la photo de l'intrus sur Telegram.
*   **La Gestion des Livreurs** : Identifiez les livreurs récurrents ou soyez alerté dès qu'un colis est déposé devant votre porte.

---

## 🧠 Détails Algorithmiques IA

Pour garantir une sécurité maximale, le système ne se contente pas d'une simple détection :

*   **Encodage Vectoriel** : Chaque visage est transformé en un vecteur de 128 dimensions. La comparaison entre deux visages est basée sur la distance Euclidienne. Un seuil (`FR_THRESHOLD`) de 0.40 est utilisé pour garantir que seules les correspondances quasi-parfaites sont acceptées.
*   **Pipeline de Traitement** :
    1.  **Capture** : Lecture du flux RTSP via OpenCV.
    2.  **Alignement** : Rotation et redimensionnement pour que les yeux soient toujours au même niveau.
    3.  **Localisation** : HOG (Histogram of Oriented Gradients) pour détecter la présence d'un visage.
    4.  **Landmarking** : Identification de 68 points clés (yeux, nez, bouche).
    5.  **Reconnaissance** : Comparaison avec la base de données `SQLCipher`.

---

## 🚀 Fonctionnalités Détaillées

### 🧠 Intelligence Artificielle (Deep Learning)
*   **Moteur Biométrique 128D** : Basé sur `dlib`, le système convertit chaque visage en un vecteur mathématique unique. La comparaison ne se fait pas sur l'image, mais sur la géométrie du visage.
*   **Multi-Frame Check (5-Frame Validation)** : Pour éviter que le portail ne s'ouvre par erreur à cause d'un oiseau ou d'un reflet, l'IA doit confirmer l'identité sur 5 images consécutives.
*   **Traitement de Flux RTSP** : Optimisé pour les caméras EZVIZ, avec gestion de la mémoire pour éviter les lags sur les flux 1080p/4K.
*   **Preprocessing OpenCV** :
    *   *Histogram Equalization* : Pour "voir" dans la pénombre.
    *   *Gaussian Blur* : Pour lisser le bruit numérique des capteurs caméra.

### 🔌 Domotique & Automatisme
*   **Protocole S7 & Modbus TCP** : Communication ultra-rapide avec le Siemens LOGO! V8.
*   **Watchdog de Connectivité** : Si le câble réseau de l'automate est débranché, l'interface WPF passe instantanément en alerte rouge et bascule en mode sécurité.
*   **Manual Override** : Un bouton "Panique" ou "Ouverture forcée" est disponible dans l'interface admin.

---

## 🛠 Architecture Système

L'application suit une structure **Clean Architecture** couplée au pattern **MVVM**.

```mermaid
graph TD
    subgraph Entrées
    A1[Webcam USB] --- B1{Sélecteur de Mode}
    A2[EZVIZ IP Cam] --- B1
    end

    subgraph Coeur de Traitement
    B1 --> C[OpenCV Processing]
    C --> D[Moteur Biométrique dlib]
    D --> E{Décision Logique}
    end

    subgraph Sorties & Actions
    E -->|Autorisé| F[Siemens LOGO! V8]
    E -->|Inconnu| G[Telegram Bot API]
    E -->|Audit| H[(SQLite + SQLCipher)]
    F --> F1[Relais: Portail]
    F --> F2[Relais: Lumières]
    end
```

---

## ⚙️ Installation & Configuration

### Prérequis Logiciels
1.  **Windows 10/11 x64**.
2.  **.NET 8.0 SDK**.
3.  **Visual Studio 2022**.

### Installation rapide

1.  **Clonage** :
    ```bash
    git clone https://github.com/othmanebenamar10/SmartSecurityIoT.git
    cd SmartSecurityIoT
    ```

2.  **Configuration des secrets** :
    Copiez `.env.example` vers `.env` et remplissez vos informations :
    ```ini
    RTSP_URL=rtsp://admin:CODE@192.168.1.XX:554
    PLC_IP=192.168.1.50
    TELEGRAM_BOT_TOKEN=VOTRE_TOKEN
    ```

3.  **Build & Run** :
    ```bash
    dotnet restore
    dotnet run --project SmartSecurityIoT.csproj
    ```

---

## 🧱 Guide Matériel (Siemens LOGO!)

1.  **Configuration Ethernet** : IP fixe (ex: `192.168.1.50`).
2.  **Modbus TCP** : Activez le serveur Modbus dans LOGO! Soft Comfort.
3.  **Mapping** :
    *   `Coil 1` (Adresse 0) -> `Q1` (Portail).
    *   `Coil 2` (Adresse 1) -> `Q2` (Lumière).

---

## 🛡️ Sécurité & Vie Privée

1.  **Cryptage SQLCipher** : La base de données est intégralement chiffrée en AES-256.
2.  **Zéro Cloud** : Vos données biométriques restent chez vous.
3.  **Hardening** : Protection contre le Brute-Force et les injections SQL.

---

## 🕹️ Modes de Fonctionnement

| Mode | Source Vidéo | Actionneur | Cas d'usage |
| :--- | :--- | :--- | :--- |
| **DEBUG / TEST** | Webcam PC | Lampe Virtuelle (UI) | Test de l'IA sur son bureau. |
| **PRODUCTION** | Caméra EZVIZ | Siemens LOGO! V8 | Installation réelle. |

---

## 📂 Structure Technique

*   **`Core/`** : Moteur de reconnaissance et logique de décision.
*   **`Services/`** : Communications (Siemens, Telegram, RTSP).
*   **`Data/`** : Couche d'accès SQLite chiffrée.
*   **`ViewModels/`** : Logique de l'interface WPF.
*   **`Views/`** : Design UI futuriste (Glassmorphism).

---

## 🚀 Roadmap

*   [ ] Détection de plaques d'immatriculation (ALPR).
*   [ ] Application mobile compagnon (.NET MAUI).
*   [ ] Analyse de posture (détection de chute).

---

## 🤝 Contribution & License

1. Forkez le projet.
2. Créez votre branche.
3. Ouvrez une Pull Request.

Distribué sous la licence **MIT**.

---
<p align="center">
  Développé avec ❤️ par <strong><a href="https://www.linkedin.com/in/benamarothmane/">Othmane BENAMAR</a></strong> pour la communauté Smart Home.
</p>