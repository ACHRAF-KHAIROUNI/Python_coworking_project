package com.coworking.app.model;

// com/coworking/app/model/Reservation.java
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalTime;

@JsonIgnoreProperties(ignoreUnknown = true)
public class Reservation {
    public long id;
    public User user;
    public Salle salle;

    @JsonProperty("date_reservation") // Lie le champ JSON à la variable Java
    public LocalDate dateReservation;

    @JsonProperty("heure_debut")
    public LocalTime heureDebut;

    @JsonProperty("heure_fin")
    public LocalTime heureFin;

    public String etat;

    @JsonProperty("prix_total")
    public BigDecimal prixTotal;
}