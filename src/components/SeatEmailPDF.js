import Styles from "../style/SeatingStyle";
import { Grid, TextField, MenuItem, Button, Dialog, DialogActions, DialogTitle, DialogContent, DialogContentText } from "@material-ui/core";
import { Alert } from '@material-ui/lab';
import React, { useState, useEffect } from "react";
import SeatLayout from "../components/SeatLayout";
import server from "../server";
import html2canvas from "html2canvas";
import { jsPDF } from "jspdf";

export default function SeatEmailPDF(props) {
    const classes = Styles.useStyles();

    const assignments = props.assignments;
    const layouts = props.layouts;
    const [selectedAssignment, setSelectedAssignment] = useState('');
    const [assignment, setAssignment] = useState(null);
    const [seatAssignment, setSeatAssignment] = useState({});
    const [seatInfo, setSeatInfo] = useState([]);
    const [rows, setRows] = useState(0);
    const [cols, setCols] = useState(0);
    const [title, setTitle] = useState('');
    const [sentEmails, setSentEmails] = useState(false);
    const [open, setOpen] = useState(false); // For the email confirmation dialog


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

        setSentEmails(false);

        let newAssignment = JSON.parse(assignment.seat_assignments);
        setSeatAssignment(newAssignment);

        let layout = findItemWithID(assignment.layout_id, layouts);
        if(layout === null) return;

        let newInfo = JSON.parse(layout.seats);
        setSeatInfo(newInfo);
        setRows(newInfo.length);
        setCols(newInfo[0].length);

        createTitle();
    }, [assignment]); // eslint-disable-line react-hooks/exhaustive-deps

    function createTitle() {
        server.getCourse(assignment.course_id)
            .then((response) => {
                let course = response.data.result;
                server.getSection(assignment.section_id)
                    .then((response) => {
                        let section = response.data.result;
                        
                        setTitle(`${course.name} ${section.section_name}: ${assignment.assignment_name}`);
                    })
                    .catch((err) => {
                        console.error(err);
                    });
            })
            .catch((err) => {
                console.error(err);
            });
    }

    function createSeatsPDF() {
        const input = document.getElementById('seats');

        html2canvas(input, input.getBoundingClientRect())
            .then((canvas) => {
                let orientation;
                if(canvas.width > canvas.height) {
                    orientation = "l";
                } else {
                    orientation = "p";
                }

                const imgData = canvas.toDataURL('image/png');
                const pdf = new jsPDF({orientation: orientation, format: [canvas.width, canvas.height]});

                pdf.addImage(imgData, 'PNG', 0, 0, canvas.width, canvas.height);
                pdf.save("seats.pdf");
            });
    }

    function createStudentsPDF() {
        // These seats are ordered by alphabetical student names
        let nameOrderedSeats = Object.keys(seatAssignment).sort((a,b) => {
            return seatAssignment[a].name < seatAssignment[b].name;
        });
        // let nameOrderedSeats = [];
        // for(let i=0; i < 100; i++) {
        //     nameOrderedSeats.push(String(i));
        // }

        createListPDF(nameOrderedSeats, "students", "Seating Chart for Students");
    }

    function createTutorsPDF() {
        // These seats are ordered alphabetically
        let seatOrderedSeats = Object.keys(seatAssignment).sort((a,b) => {
            return a < b;
        });
        // let seatOrderedSeats = [];
        // for(let i=0; i < 100; i++) {
        //     seatOrderedSeats.push(String(i));
        // }

        createListPDF(seatOrderedSeats, "tutors", "Seating Chart for Tutors")
    }

    function createListPDF(orderedSeats, saveName, description) {
        const pdf = new jsPDF('p', 'in', 'a4');
        const pdfWidth = pdf.internal.pageSize.getWidth();
        
        // Gotten from experimentation
        // Unsure how to automatically generate
        const linesPerPage = 36;

        let text;
        while(true) {
            pdf.text(title, 1, 1);
            pdf.text(description, pdfWidth/2, 1.5, {align:"center"});
            if(orderedSeats.length === 0) {
                break;
            }

            // Column One
            text = '';
            for(let i=0; i < linesPerPage; i++) {
                let seat = orderedSeats.pop();
                text += `______ ${seatAssignment[seat].name} - ${seat}\n`;
                if(orderedSeats.length === 0) {
                    break;
                }
            }
            pdf.text(text, 1, 2);

            if(orderedSeats.length === 0) {
                break;
            }

            // Column Two
            text = '';
            for(let i=0; i < linesPerPage; i++) {
                let seat = orderedSeats.pop();
                text += `______ ${seatAssignment[seat].name} - ${seat}\n`;
                if(orderedSeats.length === 0) {
                    break;
                }
            }
            pdf.text(text, pdfWidth/2, 2);

            if(orderedSeats.length === 0) {
                break;
            }

            pdf.addPage();
        }

        pdf.save(`${saveName}.pdf`);
    }

    function sendEmails() {
        setSentEmails(true);
        server.sendEmails(assignment.assignment_name)
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
            <br/><br/>
            <Grid container spacing={2}>
                <Grid item>
                    <Button variant="contained" disabled={rows === 0} onClick={createSeatsPDF}>Seats PDF</Button>
                </Grid>
                <Grid item>
                    <Button variant="contained" disabled={rows === 0} onClick={createStudentsPDF}>Students PDF</Button>
                </Grid>
                <Grid item>
                    <Button variant="contained" disabled={rows === 0} onClick={createTutorsPDF}>Tutors PDF</Button>
                </Grid>
            </Grid>
            <br/>
            <Grid container spacing={2} wrap="nowrap">
                <Grid item>
                    <Button variant="contained" disabled={sentEmails || rows === 0} onClick={() => setOpen(true)}>Send Emails</Button>
                </Grid>
                <Grid item>
                    {sentEmails && <Alert severity="success">Emails have been sent</Alert>}
                </Grid>
            </Grid>
            <br/>
            <SeatLayout
                hidden={rows === 0}
                rows={rows} cols={cols} assignment={seatAssignment}
                seatInfo={seatInfo}
            />
            <Dialog
                open={open}
                onClose={() => setOpen(false)}
            >
                <DialogTitle style={{color:"black"}}>Send an email to every student?</DialogTitle>
                <DialogContent>
                    <DialogContentText style={{color:"grey"}}>
                        Send an email notifying every student assigned a seat what their seat is.
                    </DialogContentText>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setOpen(false)} style={{color:"darkblue"}} size="large">
                        No
                    </Button>
                    <Button onClick={() => {setOpen(false); sendEmails();}} style={{color:"darkblue"}} size="large">
                        Yes
                    </Button>
                </DialogActions>
            </Dialog>
        </div>
    );
}