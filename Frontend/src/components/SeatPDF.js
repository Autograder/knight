import Styles from "../style/SeatingStyle";
import { Grid, TextField, MenuItem, Button } from "@material-ui/core";
import {  } from '@material-ui/lab';
import React, { useState, useEffect } from "react";
import SeatLayout from "../components/SeatLayout";
import {  } from "../server";
import html2canvas from "html2canvas";
import { jsPDF } from "jspdf";

export default function SeatPDF(props) {
    const classes = Styles.useStyles();

    const assignments = props.assignments;
    const layouts = props.layouts;
    const [selectedAssignment, setSelectedAssignment] = useState('');
    const [assignment, setAssignment] = useState(null);
    const [seatAssignment, setSeatAssignment] = useState({});
    const [seatInfo, setSeatInfo] = useState([]);
    const [rows, setRows] = useState(0);
    const [cols, setCols] = useState(0);


    function assignmentsToMenuItems() {
        let menuItems = [];

        for(let i=0; i < assignments.length; i++) {
            menuItems.push(
                <MenuItem value={assignments[i].id} key={assignments[i].id}>{assignments[i].assignment_name}</MenuItem>
            );
        }

        return menuItems;
    }

    function findItemWithID(id, list) {
        let item;
        for(let x of list) {
            if(x.id === id) {
                item = x;
            }
        }
        if(item === undefined) {
            return null;
        }
        return item;
    }

    useEffect(() => {
        if(selectedAssignment === '') return;

        setAssignment(findItemWithID(selectedAssignment, assignments));
    }, [selectedAssignment]); // eslint-disable-line react-hooks/exhaustive-deps

    useEffect(() => {
        if(assignment === null) return;

        let newAssignment = JSON.parse(assignment.seat_assignments);
        setSeatAssignment(newAssignment);

        let layout = findItemWithID(assignment.layout_id, layouts);
        if(layout === null) return;

        let newInfo = JSON.parse(layout.seats);
        setSeatInfo(newInfo);
        setRows(newInfo.length);
        setCols(newInfo[0].length);
    }, [assignment]); // eslint-disable-line react-hooks/exhaustive-deps

    function createSeatsPDF() {
        const input = document.getElementById('seats');

        html2canvas(input)
            .then((canvas) => {
                const imgData = canvas.toDataURL('image/png');
                const pdf = new jsPDF('p', 'px', 'a4');
                const imgProps= pdf.getImageProperties(imgData);
                const pdfWidth = pdf.internal.pageSize.getWidth();
                const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;

                pdf.addImage(imgData, 'JPEG', 0, 0, pdfWidth, pdfHeight);
                pdf.save("seats.pdf");
            });
    }

    function createStudentsPDF() {
        const pdf = new jsPDF('p', 'in', 'a4');
        const pdfWidth = pdf.internal.pageSize.getWidth();
        
        // Gotten from experimentation
        // Unsure how to automatically generate
        const linesPerPage = 40;

        // The seats are ordered by alphabetical student names
        let orderedSeats = Object.keys(seatAssignment).sort((a,b) => {
            return seatAssignment[a] < seatAssignment[b];
        });
        // let orderedSeats = [];
        // for(let i=0; i < 100; i++) {
        //     orderedSeats.push(i);
        // }

        let text;
        while(orderedSeats.length > 0) {
            // Column One
            text = '';
            for(let i=0; i < 40; i++) {
                let seat = orderedSeats.pop();
                text += `${seatAssignment[seat]} - ${seat}\n`;
                if(orderedSeats.length === 0) {
                    break;
                }
            }
            pdf.text(text, 1, 1);

            if(orderedSeats.length === 0) {
                break;
            }

            // Column Two
            text = '';
            for(let i=0; i < 40; i++) {
                let seat = orderedSeats.pop();
                text += `${seatAssignment[seat]} - ${seat}\n`;
                if(orderedSeats.length === 0) {
                    break;
                }
            }
            pdf.text(text, pdfWidth/2, 1);

            pdf.addPage();
        }

        pdf.save("students.pdf");
    }


    if(props.hidden) {
        return null;
    }

    return (
        <div className={classes.pdfMain}>
            <TextField select
                label="Load"
                value={selectedAssignment}
                onChange={(e) => setSelectedAssignment(e.target.value)}
            >
                {assignmentsToMenuItems()}
            </TextField>
            <Grid container spacing={2}>
                <Grid item>
                    <Button variant="contained" disabled={rows === 0} onClick={createSeatsPDF}>Seats PDF</Button>
                </Grid>
                <Grid item>
                    <Button variant="contained" disabled={rows === 0} onClick={createStudentsPDF}>Students PDF</Button>
                </Grid>
            </Grid>
            <SeatLayout
                hidden={rows === 0}
                rows={rows} cols={cols} assignment={seatAssignment}
                seatInfo={seatInfo}
            />
        </div>
    );
}