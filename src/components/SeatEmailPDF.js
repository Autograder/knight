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

    // An array containing the Assignments in the database
    const assignments = props.assignments;
    // An array containing the Layouts in the database
    const layouts = props.layouts;

    // This is the id of the seat assignment which has been chosen by the user
    const [selectedAssignment, setSelectedAssignment] = useState('');
    // This is the Assignment object which has been chosen by the user
    const [assignment, setAssignment] = useState(null);
    // This is the dictionary mapping seats to students of the current assignment
    const [seatAssignment, setSeatAssignment] = useState({});
    // This is the 2D seat info array of the layout corresponding to the current assignment
    const [seatInfo, setSeatInfo] = useState([]);
    // This is the number of rows in the layout
    const [rows, setRows] = useState(0);
    // This is the number of columns in the layout
    const [cols, setCols] = useState(0);

    // This is the title of the PDF that is generated, it holds info about the section and course
    const [title, setTitle] = useState('');
    // This state is used to save whether emails have been sent yet
    const [sentEmails, setSentEmails] = useState(false);
    // This state tracks whether the email confirmation dialog is open or not
    const [open, setOpen] = useState(false);


    // This function converts the array of assignments to React MenuItems
    function assignmentsToMenuItems() {
        let menuItems = [];

        for(let i=0; i < assignments.length; i++) {
            menuItems.push(
                <MenuItem value={assignments[i].id} key={assignments[i].id}>{assignments[i].assignment_name}</MenuItem>
            );
        }

        return menuItems;
    }

    // This function finds an item in an array with a corresponding ID
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

    // Whenever the user selects a different assignment we want to update the Assignment object
    useEffect(() => {
        if(selectedAssignment === '') return;

        setAssignment(findItemWithID(selectedAssignment, assignments));
    }, [selectedAssignment]); // eslint-disable-line react-hooks/exhaustive-deps

    // Whenever the Assignment object updates we want to get corresponding info about the Layout
    useEffect(() => {
        if(assignment === null) return;

        // Assume emails haven't been sent for this new layout
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

    // Here is where we do the database queries about the course and section in order to create a title for the PDF
    function createTitle() {
        // Search for the course
        server.getCourse(assignment.course_id)
            .then((response) => {
                // Save the Course object we found
                let course = response.data.result;

                // Now look query for the section
                server.getSection(assignment.section_id)
                    .then((response) => {
                        // Save the Section object we found
                        let section = response.data.result;
                        
                        // Set the title to reflect the info we found
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

    // Here is where we turn the React SeatLayout element into an image then PDF format
    function createSeatsPDF() {
        // The SeatLayout should have an id of seats
        const input = document.getElementById('seats');

        // This creates a Canvas object
        html2canvas(input, input.getBoundingClientRect())
            .then((canvas) => {
                // Weird things happen if we don't manually calculate orientation like this
                let orientation;
                if(canvas.width > canvas.height) {
                    // landscape (horizontal) orientation
                    orientation = "l";
                } else {
                    // portrait (verical) orientation
                    orientation = "p";
                }

                // tbh I'm not entirely sure how this all works, but it does work
                const imgData = canvas.toDataURL('image/png');
                const pdf = new jsPDF({orientation: orientation, format: [canvas.width, canvas.height]});

                pdf.addImage(imgData, 'PNG', 0, 0, canvas.width, canvas.height);
                // You can change the name of the PDF to be whatever you want
                pdf.save("seats.pdf");
            });
    }

    // Uses the createListPDF function to create a PDF for students to use
    function createStudentsPDF() {
        // These seats are ordered by alphabetical student names
        // Students will be looking for their name, so we want the names ordered alphabetically
        let nameOrderedSeats = Object.keys(seatAssignment).sort((a,b) => {
            return seatAssignment[a].name < seatAssignment[b].name;
        });

        // nameOrderedSeats is the sorted array we're providing
        // students is the name of the generated PDF
        // Seating Chart for Students is used as a header at the top of the PDF
        createListPDF(nameOrderedSeats, "students", "Seating Chart for Students");
    }

    // Uses the createListPDF function to create a PDF for tutors to use
    function createTutorsPDF() {
        // These seats are ordered alphabetically
        // Tutors will be looking for a specific seat, so we want the seats ordered alphabetically
        let seatOrderedSeats = Object.keys(seatAssignment).sort((a,b) => {
            return a < b;
        });

        // seatOrderedSeats is the sorted array we're providing
        // tutors is the name of the generated PDF
        // Seating Chart for Tutors is used as a header at the top of the PDF
        createListPDF(seatOrderedSeats, "tutors", "Seating Chart for Tutors")
    }

    // This function generates a PDF based on a sorting function, a name for the PDF, and a header description
    // orderedSeats is a list of seats which is sorted in the order that we want the seats to appear on the PDF
    //     Doesn't include the students in the seats, we'll use the assignment dictionary for that
    function createListPDF(orderedSeats, saveName, description) {
        // portrait mode, units in inches, a4 size of PDF
        const pdf = new jsPDF('p', 'in', 'a4');
        const pdfWidth = pdf.internal.pageSize.getWidth();
        
        // Gotten from experimentation
        // Unsure how to automatically generate
        const linesPerPage = 36;

        // text is where we'll save the body text of the PDF
        let text;
        while(true) {
            // First we can put the title and description heading at the top of the page
            pdf.text(title, 1, 1);
            pdf.text(description, pdfWidth/2, 1.5, {align:"center"});

            // We're going to pop items off of the list of seats
            // We're checking to make sure any seats are left
            if(orderedSeats.length === 0) {
                break;
            }

            // Column One
            // Add linesPerPage number of students to the first column
            text = '';
            for(let i=0; i < linesPerPage; i++) {
                let seat = orderedSeats.pop();

                // We leave a blank space at the beginning for people to mark off
                text += `______ ${seatAssignment[seat].name} - ${seat}\n`;

                // If we don't have any seat assignments left to add to the PDF, break
                if(orderedSeats.length === 0) {
                    break;
                }
            }
            // Put the generated text onto the PDF
            pdf.text(text, 1, 2);

            if(orderedSeats.length === 0) {
                break;
            }

            // Column Two
            // If there are still students remaining add linesPerPage number of students to the second column
            text = '';
            for(let i=0; i < linesPerPage; i++) {
                let seat = orderedSeats.pop();

                // We leave a blank space at the beginning for people to mark off
                text += `______ ${seatAssignment[seat].name} - ${seat}\n`;

                // If we don't have any seat assignments left to add to the PDF, break
                if(orderedSeats.length === 0) {
                    break;
                }
            }
            // Put the generated text onto the PDF
            pdf.text(text, pdfWidth/2, 2);

            if(orderedSeats.length === 0) {
                break;
            }

            // If there are still students remaining create a new page
            pdf.addPage();
        }

        // Save the pdf with the saveName given
        pdf.save(`${saveName}.pdf`);
    }

    // Function to send the emails out to assigned students
    function sendEmails() {
        setSentEmails(true);
        server.sendEmails(assignment.assignment_name)
    }


    // If passed a hidden prop, return null
    if(props.hidden) {
        return null;
    }

    return (
        <div className={classes.pdfMain}>
            {/* The drop down menu to select an assignment */}
            <TextField select
                label="Load"
                value={selectedAssignment}
                onChange={(e) => setSelectedAssignment(e.target.value)}
            >
                {/* The MenuItems are generated dynamically with this function */}
                {assignmentsToMenuItems()}
            </TextField>
            <br/><br/>

            {/* The different buttons to generate PDFs */}
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

            {/* The button to send emails and a notifying alert to show that they've been sent */}
            <Grid container spacing={2} wrap="nowrap">
                <Grid item>
                    <Button variant="contained" disabled={sentEmails || rows === 0} onClick={() => setOpen(true)}>Send Emails</Button>
                </Grid>
                <Grid item>
                    {sentEmails && <Alert severity="success">Emails have been sent</Alert>}
                </Grid>
            </Grid>
            <br/>

            {/* The seat display */}
            <SeatLayout
                hidden={rows === 0}
                rows={rows} cols={cols} assignment={seatAssignment}
                seatInfo={seatInfo}
            />

            {/* The dialog that appears to confirm that you want to send an email */}
            <Dialog
                open={open}
                onClose={() => setOpen(false)}
            >
                <DialogTitle style={{color:"black"}}>Send an email to every student?</DialogTitle>
                <DialogContent>
                    <DialogContentText style={{color:"grey"}}>
                        Send an email notifying every student assigned a seat what their seat is.
                        (Yes this is currently functioning)
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