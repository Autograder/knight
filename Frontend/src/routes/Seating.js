import OurTheme from "../style/Theme";
import Styles from "../style/SeatingStyle";
import { ThemeProvider } from "@material-ui/styles";
import { Tabs, Tab } from "@material-ui/core";
import {  } from '@material-ui/lab';
import React, { useState } from "react";
import LayoutEditor from "../components/LayoutEditor";
import SeatAssign from "../components/SeatAssign";

export default function Seating() {
    const classes = Styles.useStyles();
    const theme = OurTheme.theme;

    const [selectedTab, setSelectedTab] = useState(0);

    return (
        <div className={classes.root}>
            <ThemeProvider theme={theme}>
                <Tabs value={selectedTab} onChange={(e, v) => setSelectedTab(v)}>
                    <Tab label="Layout Editor" value={0} />
                    <Tab label="Assign Seats" value={1} />
                </Tabs>
                <LayoutEditor hidden={selectedTab != 0} />
                <SeatAssign hidden={selectedTab != 1} />
            </ThemeProvider>
        </div>
    )
}