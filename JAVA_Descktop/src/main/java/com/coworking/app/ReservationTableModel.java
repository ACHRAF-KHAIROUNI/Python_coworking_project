package com.coworking.app;

// com/coworking/app/ReservationTableModel.java
import com.coworking.app.model.Reservation;
import javax.swing.table.AbstractTableModel;
import java.util.List;

public class ReservationTableModel extends AbstractTableModel {
    private final List<Reservation> reservations;
    private final String[] columnNames = {"ID", "Client", "Salle", "Date", "Créneau", "État"};

    public ReservationTableModel(List<Reservation> reservations) {
        this.reservations = reservations;
    }

    @Override public int getRowCount() { return reservations.size(); }
    @Override public int getColumnCount() { return columnNames.length; }
    @Override public String getColumnName(int column) { return columnNames[column]; }

    @Override
    public Object getValueAt(int rowIndex, int columnIndex) {
        Reservation reservation = reservations.get(rowIndex);
        switch (columnIndex) {
            case 0: return reservation.id;
            case 1: return reservation.user.username;
            case 2: return reservation.salle.nom;
            case 3: return reservation.dateReservation.toString();
            case 4: return reservation.heureDebut + " - " + reservation.heureFin;
            case 5: return reservation.etat;
            default: return null;
        }
    }
}
