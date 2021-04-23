import OurTheme from "../style/Theme";
import Styles from "../style/SeatingStyle";
import { ThemeProvider } from "@material-ui/styles";
import { Grid, TextField, MenuItem, Button, InputLabel } from "@material-ui/core";
import { ToggleButton, ToggleButtonGroup, Alert } from '@material-ui/lab';
import React, { useState, useEffect } from "react";
import LayoutEditor from "../components/LayoutEditor";

export default function Seating() {
    const classes = Styles.useStyles();
    const theme = OurTheme.theme;

    return (
        <div className={classes.root}>
            <ThemeProvider theme={theme}>
                <LayoutEditor />
            </ThemeProvider>
        </div>
    )
}