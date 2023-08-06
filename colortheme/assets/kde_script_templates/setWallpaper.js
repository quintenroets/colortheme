let desktop = desktops()[0];
desktop.wallpaperPlugin = "org.kde.image";
desktop.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");
desktop.writeConfig("Image", "IMAGE_PATH");
desktop.reloadConfig();
