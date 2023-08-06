let desktop = desktops()[0];
desktop.wallpaperPlugin = "org.kde.image";
desktop.currentConfigGroup = Array('Wallpaper', 'org.kde.image', 'General');
image = desktop.readConfig('Image');
print(image);
