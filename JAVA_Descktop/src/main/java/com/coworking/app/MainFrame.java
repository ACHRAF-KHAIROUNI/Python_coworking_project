package com.coworking.app;

import com.coworking.app.model.ApiService;
import com.coworking.app.model.Reservation;
import com.coworking.app.model.*;
import com.coworking.app.model.Salle;
import com.formdev.flatlaf.extras.FlatSVGIcon;
import com.github.lgooddatepicker.components.DatePicker;
import com.github.lgooddatepicker.components.DatePickerSettings;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;
import java.time.LocalDate;
import java.util.Collections;
import java.util.List;

public class MainFrame extends JFrame {

    private final ApiService apiService;
    private final JTable reservationTable;
    private ReservationTableModel tableModel;

    private final JButton completeButton;
    private final JButton cancelButton;
    private final DatePicker datePicker;
    private final JComboBox<Salle> salleComboBox;
    private final JLabel statusBar;

    public MainFrame(ApiService apiService) {
        this.apiService = apiService;

        setTitle("Tableau de Bord - Coworking Admin");
        setIconImage(new FlatSVGIcon("com/coworking/app/icons/logo.svg", 16, 16).getImage());
        setSize(1100, 700);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        JPanel mainPanel = new JPanel(new BorderLayout(10, 10));
        mainPanel.setBorder(new EmptyBorder(10, 10, 10, 10));

        // 1. Barre d'outils en haut (avec les filtres)
        JToolBar toolBar = new JToolBar();
        toolBar.setFloatable(false);
        toolBar.setBorder(new EmptyBorder(0,0,5,0));

        DatePickerSettings dateSettings = new DatePickerSettings();
        dateSettings.setAllowKeyboardEditing(false);
        datePicker = new DatePicker(dateSettings);

        salleComboBox = new JComboBox<>();
        salleComboBox.setPreferredSize(new Dimension(200, datePicker.getPreferredSize().height));

        JButton filterButton = new JButton("Filtrer");
        JButton resetButton = new JButton("Réinitialiser");

        toolBar.add(new JLabel("Date: "));
        toolBar.add(datePicker);
        toolBar.add(Box.createHorizontalStrut(15));
        toolBar.add(new JLabel("Salle: "));
        toolBar.add(salleComboBox);
        toolBar.add(Box.createHorizontalStrut(10));
        toolBar.add(filterButton);
        toolBar.add(resetButton);

        mainPanel.add(toolBar, BorderLayout.NORTH);

        // 2. Tableau des réservations au centre
        reservationTable = new JTable();
        reservationTable.setRowHeight(28);
        reservationTable.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        reservationTable.setFillsViewportHeight(true);
        reservationTable.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);



        JScrollPane scrollPane = new JScrollPane(reservationTable);
        mainPanel.add(scrollPane, BorderLayout.CENTER);

        // 3. Panneau d'actions à droite
        JPanel actionPanel = new JPanel();
        actionPanel.setLayout(new BoxLayout(actionPanel, BoxLayout.Y_AXIS));
        actionPanel.setBorder(BorderFactory.createTitledBorder("Actions sur la sélection"));
        actionPanel.setPreferredSize(new Dimension(220, 0));

        completeButton = new JButton("✔  Marquer comme Terminée");
        cancelButton = new JButton("✖  Annuler la Réservation");
        updateButtonState();

        actionPanel.add(completeButton);
        actionPanel.add(Box.createRigidArea(new Dimension(0, 10)));
        actionPanel.add(cancelButton);
        mainPanel.add(actionPanel, BorderLayout.EAST);

        // 4. Barre de statut en bas
        statusBar = new JLabel("Prêt.");
        statusBar.setBorder(new EmptyBorder(4, 4, 4, 4));
        mainPanel.add(statusBar, BorderLayout.SOUTH);

        add(mainPanel);

        // --- GESTION DES ÉVÉNEMENTS ---
        reservationTable.getSelectionModel().addListSelectionListener(e -> updateButtonState());
        filterButton.addActionListener(e -> loadReservations());
        resetButton.addActionListener(e -> {
            datePicker.clear();
            salleComboBox.setSelectedIndex(0);
            loadReservations();
        });
        completeButton.addActionListener(e -> handleCompleteReservation());
        cancelButton.addActionListener(e -> handleCancelReservation());

        // --- CHARGEMENT INITIAL ---
        loadSallesForFilter();
        loadReservations();
    }

    private void updateButtonState() {
        boolean rowSelected = reservationTable.getSelectedRow() != -1;
        completeButton.setEnabled(rowSelected);
        cancelButton.setEnabled(rowSelected);
    }

    private void loadSallesForFilter() {
        new SwingWorker<List<Salle>, Void>() {
            @Override
            protected List<Salle> doInBackground() throws Exception {
                return apiService.getSalles();
            }

            @Override
            protected void done() {
                try {
                    List<Salle> salles = get();
                    salleComboBox.removeAllItems();
                    salleComboBox.addItem(new Salle(-1, "Toutes les salles"));
                    for (Salle salle : salles) {
                        salleComboBox.addItem(salle);
                    }
                } catch (Exception e) {
                    salleComboBox.removeAllItems();
                    salleComboBox.addItem(new Salle(-1, "Erreur chargement"));
                    e.printStackTrace();
                }
            }
        }.execute();
    }

    private void loadReservations() {
        statusBar.setText("Chargement des réservations...");
        LocalDate selectedDate = datePicker.getDate();
        Salle selectedSalle = (Salle) salleComboBox.getSelectedItem();
        Long salleId = (selectedSalle != null && selectedSalle.id != -1) ? selectedSalle.id : null;

        new SwingWorker<List<Reservation>, Void>() {
            @Override
            protected List<Reservation> doInBackground() throws Exception {
                return apiService.getReservations(selectedDate, salleId);
            }

            @Override
            protected void done() {
                try {
                    List<Reservation> reservations = get();
                    tableModel = new ReservationTableModel(reservations);
                    reservationTable.setModel(tableModel);

                    // --- CORRECTION : ON APPLIQUE LE RENDERER ICI ---
                    // On vérifie d'abord que le tableau a assez de colonnes
                    if (reservationTable.getColumnCount() > 5) {
                        // On applique notre renderer personnalisé à la 6ème colonne (index 5)
                        reservationTable.getColumnModel().getColumn(5).setCellRenderer(new StatusCellRenderer());
                        // On peut aussi définir la largeur de la colonne
                        reservationTable.getColumnModel().getColumn(5).setPreferredWidth(100);
                        reservationTable.getColumnModel().getColumn(0).setPreferredWidth(40); // Pour l'ID
                    }
                    // ---------------------------------------------

                    statusBar.setText(reservations.size() + " réservation(s) chargée(s).");
                } catch (Exception e) {
                    statusBar.setText("Erreur de chargement des réservations.");
                    JOptionPane.showMessageDialog(MainFrame.this,
                            "Erreur de chargement : " + e.getCause().getMessage(),
                            "Erreur Réseau", JOptionPane.ERROR_MESSAGE);
                    e.printStackTrace();
                }
            }
        }.execute();
    }

    private long getSelectedReservationId() {
        int selectedRow = reservationTable.getSelectedRow();
        if (selectedRow == -1) {
            JOptionPane.showMessageDialog(this, "Veuillez sélectionner une réservation dans le tableau.", "Aucune sélection", JOptionPane.WARNING_MESSAGE);
            return -1;
        }
        return (long) tableModel.getValueAt(selectedRow, 0);
    }

    private void handleCompleteReservation() {
        long reservationId = getSelectedReservationId();
        if (reservationId == -1) return;

        statusBar.setText("Action en cours...");
        new SwingWorker<Void, Void>() {
            @Override
            protected Void doInBackground() throws Exception {
                apiService.completeReservation(reservationId);
                return null;
            }

            @Override
            protected void done() {
                try {
                    get();
                    statusBar.setText("Action réussie.");
                    JOptionPane.showMessageDialog(MainFrame.this, "La réservation a bien été marquée comme terminée.", "Succès", JOptionPane.INFORMATION_MESSAGE);
                    loadReservations();
                } catch (Exception e) {
                    statusBar.setText("Action échouée.");
                    JOptionPane.showMessageDialog(MainFrame.this, "Erreur : " + e.getCause().getMessage(), "Erreur", JOptionPane.ERROR_MESSAGE);
                }
            }
        }.execute();
    }

    private void handleCancelReservation() {
        long reservationId = getSelectedReservationId();
        if (reservationId == -1) return;

        int confirm = JOptionPane.showConfirmDialog(this,
                "Êtes-vous sûr de vouloir annuler cette réservation ?\nCette action est irréversible.",
                "Confirmation d'annulation", JOptionPane.YES_NO_OPTION);

        if (confirm != JOptionPane.YES_OPTION) {
            return;
        }

        statusBar.setText("Annulation en cours...");
        new SwingWorker<String, Void>() {
            @Override
            protected String doInBackground() throws Exception {
                return apiService.cancelReservation(reservationId);
            }

            @Override
            protected void done() {
                try {
                    String successMessage = get();
                    statusBar.setText("Action réussie.");
                    JOptionPane.showMessageDialog(MainFrame.this, successMessage, "Succès", JOptionPane.INFORMATION_MESSAGE);
                    loadReservations();
                } catch (Exception e) {
                    statusBar.setText("Action échouée.");
                    JOptionPane.showMessageDialog(MainFrame.this, "Erreur : " + e.getCause().getMessage(), "Erreur", JOptionPane.ERROR_MESSAGE);
                }
            }
        }.execute();
    }
}

