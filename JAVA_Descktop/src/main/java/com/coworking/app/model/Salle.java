package com.coworking.app.model;

// com/coworking/app/model/Salle.java
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true)
// com/coworking/app/model/Salle.java
public class Salle {
    public long id;
    public String nom;

    // Constructeur vide requis par Jackson
    public Salle() {}

    // Constructeur pour l'item "Toutes les salles"
    public Salle(long id, String nom) {
        this.id = id;
        this.nom = nom;
    }

    // Surcharger toString pour un affichage correct dans le JComboBox
    @Override
    public String toString() {
        return nom;
    }
}