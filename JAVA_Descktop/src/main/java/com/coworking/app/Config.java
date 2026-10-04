package com.coworking.app;

// com/coworking/app/Config.java
import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

public class Config {
    private static final Properties properties = new Properties();

    // Ce bloc 'static' est exécuté une seule fois, au chargement de la classe
    static {
        try (InputStream input = Config.class.getClassLoader().getResourceAsStream("config.properties")) {
            if (input == null) {
                System.out.println("Désolé, impossible de trouver le fichier config.properties");
            }
            // Charger le fichier de propriétés
            properties.load(input);
        } catch (IOException ex) {
            ex.printStackTrace();
        }
    }

    public static String getApiBaseUrl() {
        // Récupérer la propriété, avec une valeur par défaut au cas où
        return properties.getProperty("api.base.url", "http://127.0.0.1:8000/api");
    }
}
