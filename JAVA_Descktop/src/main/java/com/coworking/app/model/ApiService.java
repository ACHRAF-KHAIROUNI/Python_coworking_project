package com.coworking.app.model;


import com.coworking.app.Config;
import com.coworking.app.model.Reservation;
import com.coworking.app.model.Salle;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.PropertyNamingStrategies;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import okhttp3.*;

import java.io.IOException;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.List;

public class ApiService {
    private static final OkHttpClient client = new OkHttpClient();
    private static final ObjectMapper objectMapper = new ObjectMapper()
            .registerModule(new JavaTimeModule())
            .setPropertyNamingStrategy(PropertyNamingStrategies.SNAKE_CASE);

    private static final String BASE_URL = Config.getApiBaseUrl();
    private String accessToken;

    public boolean login(String username, String password) throws IOException {
        String jsonBody = "{\"username\": \"" + username + "\", \"password\": \"" + password + "\"}";
        RequestBody body = RequestBody.create(jsonBody, MediaType.get("application/json; charset=utf-8"));

        Request request = new Request.Builder()
                .url(BASE_URL + "/token/")
                .post(body)
                .build();

        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                return false;
            }
            JsonNode rootNode = objectMapper.readTree(response.body().string());
            this.accessToken = rootNode.get("access").asText();
            return this.accessToken != null && !this.accessToken.isEmpty();
        }
    }

    public List<Reservation> getReservations(LocalDate date, Long salleId) throws IOException {
        if (accessToken == null) {
            throw new IOException("Non authentifié.");
        }

        // Construire l'URL avec les paramètres de requête
        HttpUrl.Builder urlBuilder = HttpUrl.parse(BASE_URL + "/reservations/").newBuilder();
        if (date != null) {
            // Formater la date au format AAAA-MM-JJ attendu par l'API
            urlBuilder.addQueryParameter("date", date.format(DateTimeFormatter.ISO_LOCAL_DATE));
        }
        if (salleId != null) {
            urlBuilder.addQueryParameter("salle_id", String.valueOf(salleId));
        }

        Request request = new Request.Builder()
                .url(urlBuilder.build()) // Utiliser l'URL construite
                .header("Authorization", "Bearer " + accessToken)
                .build();

        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new IOException("Erreur lors de la récupération des réservations : " + response.code());
            }
            return objectMapper.readValue(response.body().string(), new TypeReference<List<Reservation>>() {});
        }
    }

    public Reservation completeReservation(long reservationId) throws IOException {
        if (accessToken == null) throw new IOException("Non authentifié.");

        RequestBody body = RequestBody.create(new byte[0], null);

        Request request = new Request.Builder()
                .url(BASE_URL + "/reservations/" + reservationId + "/complete/")
                .header("Authorization", "Bearer " + accessToken)
                .post(body)
                .build();

        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                String errorBody = response.body() != null ? response.body().string() : "Erreur inconnue";
                throw new IOException("Échec de l'opération 'terminer': " + errorBody);
            }
            return objectMapper.readValue(response.body().string(), Reservation.class);
        }
    }

    public String cancelReservation(long reservationId) throws IOException {
        if (accessToken == null) throw new IOException("Non authentifié.");

        RequestBody body = RequestBody.create(new byte[0], null);

        Request request = new Request.Builder()
                .url(BASE_URL + "/reservations/" + reservationId + "/cancel/")
                .header("Authorization", "Bearer " + accessToken)
                .post(body)
                .build();

        try (Response response = client.newCall(request).execute()) {
            String responseBody = response.body() != null ? response.body().string() : "{}";
            if (!response.isSuccessful()) {
                throw new IOException("Échec de l'annulation: " + responseBody);
            }
            JsonNode rootNode = objectMapper.readTree(responseBody);
            return rootNode.has("success") ? rootNode.get("success").asText() : "Opération réussie.";
        }
    }
    public List<Salle> getSalles() throws IOException {
        if (accessToken == null) {
            throw new IOException("Non authentifié.");
        }

        Request request = new Request.Builder()
                .url(BASE_URL + "/salles/")
                .header("Authorization", "Bearer " + accessToken)
                .build();

        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new IOException("Erreur lors de la récupération des salles : " + response.code());
            }
            return objectMapper.readValue(response.body().string(), new TypeReference<List<Salle>>() {});
        }
    }

}

