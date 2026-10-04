// com/coworking/app/StatusCellRenderer.java
package com.coworking.app;

import javax.swing.*;
import javax.swing.table.DefaultTableCellRenderer;
import java.awt.*;

public class StatusCellRenderer extends DefaultTableCellRenderer {

    // Couleurs que nous allons utiliser
    private static final Color PENDING_BG = new Color(255, 243, 205); // Jaune clair
    private static final Color PENDING_FG = new Color(133, 100, 4);   // Jaune foncé
    private static final Color CONFIRMED_BG = new Color(212, 237, 218); // Vert clair
    private static final Color CONFIRMED_FG = new Color(21, 87, 36);    // Vert foncé
    private static final Color COMPLETED_BG = new Color(209, 236, 241); // Bleu clair
    private static final Color COMPLETED_FG = new Color(12, 84, 96);    // Bleu foncé
    private static final Color CANCELLED_BG = new Color(248, 215, 218); // Rouge clair
    private static final Color CANCELLED_FG = new Color(114, 28, 36);   // Rouge foncé

    @Override
    public Component getTableCellRendererComponent(JTable table, Object value,
                                                   boolean isSelected, boolean hasFocus,
                                                   int row, int column) {

        // On appelle d'abord la méthode parente pour obtenir le composant de base (un JLabel)
        Component c = super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column);

        if (value instanceof String) {
            String status = (String) value;

            // Centrer le texte pour un meilleur rendu
            setHorizontalAlignment(JLabel.CENTER);

            // Appliquer les couleurs en fonction du statut
            switch (status.toUpperCase()) {
                case "PENDING":
                    c.setBackground(PENDING_BG);
                    c.setForeground(PENDING_FG);
                    break;
                case "CONFIRMED":
                    c.setBackground(CONFIRMED_BG);
                    c.setForeground(CONFIRMED_FG);
                    break;
                case "COMPLETED":
                    c.setBackground(COMPLETED_BG);
                    c.setForeground(COMPLETED_FG);
                    break;
                case "CANCELLED":
                    c.setBackground(CANCELLED_BG);
                    c.setForeground(CANCELLED_FG);
                    break;
                default:
                    // Si le statut est inconnu ou si la cellule est sélectionnée, on utilise les couleurs par défaut
                    c.setBackground(table.getBackground());
                    c.setForeground(table.getForeground());
            }
        }

        // Si la ligne est sélectionnée, on utilise les couleurs de sélection pour ne pas perdre la visibilité
        if (isSelected) {
            c.setBackground(table.getSelectionBackground());
            c.setForeground(table.getSelectionForeground());
        }

        return c;
    }
}