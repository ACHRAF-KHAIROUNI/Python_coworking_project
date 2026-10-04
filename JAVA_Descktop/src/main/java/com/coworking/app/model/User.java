package com.coworking.app.model;

// com/coworking/app/model/User.java
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true) // Ignore les champs JSON non définis ici
public class User {
    public long id;
    public String username;
    public String first_name;
    public String last_name;
}
