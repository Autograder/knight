import OurTheme from "../style/Theme";
import Styles from "../style/SeatingStyle";
import { ThemeProvider } from "@material-ui/styles";
import { Tabs, Tab } from "@material-ui/core";
import React, { useState, useEffect } from "react";
import LayoutEditor from "../components/LayoutEditor";
import SeatAssign from "../components/SeatAssign";
import server from "../server"

export default function Seating() {
    const classes = Styles.useStyles();
    const theme = OurTheme.theme;

    const [selectedTab, setSelectedTab] = useState(0);
    const [layouts, setLayouts] = useState([]);
    const [assignments, setAssignments] = useState([]);

    function updateLayouts() {
        server.getLayouts()
            .then((response) => {
                let newLayouts = response.data.result;
                setLayouts(newLayouts);
            })
            .catch((err) => {
                console.error(err);
            });
    }

    function updateAssignments() {
        server.getSeatAssignments()
            .then((response) => {
                let newAssignments = response.data.result;
                setAssignments(newAssignments);
            })
            .catch((err) => {
                console.error(err);
            });
    }

    useEffect(() => {
        updateLayouts();
        updateAssignments();
    }, []);

    return (
        <div className={classes.root}>
            <ThemeProvider theme={theme}>
                <Tabs value={selectedTab} onChange={(e, v) => setSelectedTab(v)}>
                    <Tab label="Layout Editor" value={0} />
                    <Tab label="Assign Seats" value={1} />
                </Tabs>
                <LayoutEditor hidden={selectedTab !== 0} layouts={layouts} updateLayouts={updateLayouts} />
                <SeatAssign hidden={selectedTab !== 1} layouts={layouts} assignments={assignments} updateAssignments={updateAssignments}/>
            </ThemeProvider>
        </div>
    );
}