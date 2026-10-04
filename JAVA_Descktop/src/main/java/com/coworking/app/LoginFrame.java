package com.coworking.app;

// com/coworking/app/LoginFrame.java
// Dans le package com.coworking.app

import com.coworking.app.model.ApiService;
import com.formdev.flatlaf.extras.FlatSVGIcon;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;
import java.io.IOException;

import com.coworking.app.*;
import com.coworking.app.model.*;
public class LoginFrame extends JFrame {

    private final JTextField usernameField;
    private final JPasswordField passwordField;
    private final JButton loginButton;
    private final JLabel statusLabel;

    public LoginFrame() {
        setTitle("Coworking Admin - Connexion");
        // Charge une icône depuis le dossier resources. Créez les dossiers et placez-y une icône.
        // Chemin attendu : src/main/resources/com/coworking/app/icons/logo.svg
        setIconImage(new FlatSVGIcon("com/coworking/app/icons/logo.svg", 16, 16).getImage());
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setResizable(false);

        // Panneau principal avec des marges
        JPanel mainPanel = new JPanel(new BorderLayout(15, 15));
        mainPanel.setBorder(new EmptyBorder(20, 20, 20, 20));

        // Titre en haut
        JLabel titleLabel = new JLabel("Authentification", SwingConstants.CENTER);
        titleLabel.setFont(new Font("Segoe UI", Font.BOLD, 24));
        mainPanel.add(titleLabel, BorderLayout.NORTH);

        // Panneau pour les champs de formulaire, bien alignés
        JPanel fieldsPanel = new JPanel(new GridBagLayout());
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(5, 5, 5, 5);
        gbc.fill = GridBagConstraints.HORIZONTAL;

        gbc.gridx = 0; gbc.gridy = 0;
        fieldsPanel.add(new JLabel("Utilisateur :"), gbc);

        gbc.gridx = 1; gbc.gridy = 0;
        usernameField = new JTextField(20);
        fieldsPanel.add(usernameField, gbc);

        gbc.gridx = 0; gbc.gridy = 1;
        fieldsPanel.add(new JLabel("Mot de passe :"), gbc);

        gbc.gridx = 1; gbc.gridy = 1;
        passwordField = new JPasswordField(20);
        fieldsPanel.add(passwordField, gbc);

        mainPanel.add(fieldsPanel, BorderLayout.CENTER);

        // Panneau pour le bouton et le statut
        JPanel bottomPanel = new JPanel(new BorderLayout(0, 5));
        loginButton = new JButton("Se connecter");
        loginButton.putClientProperty("JButton.buttonType", "roundRect"); // Style FlatLaf

        statusLabel = new JLabel(" ", SwingConstants.CENTER);
        statusLabel.setForeground(Color.RED);

        bottomPanel.add(loginButton, BorderLayout.CENTER);
        bottomPanel.add(statusLabel, BorderLayout.SOUTH);

        mainPanel.add(bottomPanel, BorderLayout.SOUTH);

        add(mainPanel);

        pack(); // Ajuste la taille de la fenêtre au contenu
        setLocationRelativeTo(null); // Centre la fenêtre

        // Action sur le bouton
        loginButton.addActionListener(e -> handleLogin());
    }

    // com/coworking/app/LoginFrame.java

    private void handleLogin() {
        String username = usernameField.getText();
        String password = new String(passwordField.getPassword());

        if (username.isEmpty() || password.isEmpty()) {
            statusLabel.setText("Veuillez remplir tous les champs.");
            return;
        }

        // Mettre à jour l'interface AVANT de lancer la tâche de fond
        loginButton.setEnabled(false);
        statusLabel.setForeground(Color.BLACK);
        statusLabel.setText("Connexion en cours...");

        new SwingWorker<ApiService, Void>() {
            private String errorMessage = null; // Pour stocker un message d'erreur

            @Override
            protected ApiService doInBackground() {
                try {
                    ApiService apiService = new ApiService();
                    boolean success = apiService.login(username, password);
                    if (success) {
                        return apiService; // Succès, on retourne l'objet service
                    } else {
                        // Les identifiants sont probablement incorrects
                        errorMessage = "Nom d'utilisateur ou mot de passe incorrect.";
                        return null;
                    }
                } catch (IOException e) {
                    // Erreur réseau (serveur non démarré, pas de connexion, etc.)
                    errorMessage = "Erreur réseau. Impossible de joindre le serveur.";
                    e.printStackTrace(); // Très utile pour voir l'erreur dans la console
                    return null;
                } catch (Exception e) {
                    // Toute autre erreur inattendue
                    errorMessage = "Une erreur inattendue est survenue.";
                    e.printStackTrace();
                    return null;
                }
            }

            @Override
            protected void done() {
                try {
                    ApiService loggedInService = get(); // Récupère le résultat de doInBackground()

                    if (loggedInService != null) {
                        // CAS DE SUCCÈS
                        MainFrame mainFrame = new MainFrame(loggedInService);
                        mainFrame.setVisible(true);
                        dispose(); // Ferme la fenêtre de login
                    } else {
                        // CAS D'ÉCHEC
                        statusLabel.setForeground(Color.RED);
                        // Affiche le message d'erreur que nous avons défini
                        statusLabel.setText(errorMessage != null ? errorMessage : "Échec de la connexion.");
                    }
                } catch (Exception e) {
                    // Ce catch est une sécurité supplémentaire
                    statusLabel.setForeground(Color.RED);
                    statusLabel.setText("Erreur lors de la finalisation de la connexion.");
                    e.printStackTrace();
                } finally {
                    // Dans tous les cas, on réactive le bouton
                    loginButton.setEnabled(true);
                }
            }
        }.execute();
    }
}