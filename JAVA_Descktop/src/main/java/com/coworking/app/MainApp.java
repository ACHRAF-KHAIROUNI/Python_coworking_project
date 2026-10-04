package com.coworking.app;

// com/coworking/app/MainApp.java
import com.formdev.flatlaf.FlatLightLaf;
import com.coworking.app.LoginFrame; // <-- Vérifiez cet import

import javax.swing.SwingUtilities;

public class MainApp {
    public static void main(String[] args) {
        FlatLightLaf.setup();
        SwingUtilities.invokeLater(() -> {
            LoginFrame loginFrame = new LoginFrame();
            loginFrame.setVisible(true);
        });
    }
}
