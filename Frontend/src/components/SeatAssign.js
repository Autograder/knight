import Styles from "../style/SeatingStyle";
import {  } from "@material-ui/core";
import {  } from '@material-ui/lab';
import React, { useState } from "react";
import SeatLayout from "./SeatLayout";
import server from "../server"

export default function SeatAssign(props) {
    if(props.hidden) {
        return null;
    }

    return (
        "This is the Seat Assign"
    )
}