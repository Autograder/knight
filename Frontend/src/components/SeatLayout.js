import Styles from "../style/SeatingStyle";
import { Grid, Box } from "@material-ui/core";
import React from "react";

export default function SeatLayout(props) {
    const classes = Styles.useStyles();

    if(props.hidden) {
        return null;
    }

    let seats2D = [];
    for(let i=0; i < props.rows; i++) {
        let row = [];

        for(let j=0; j < props.cols; j++) {
            let seatInfo = props.seatInfo[i][j];
            let className = ` ${classes.seat}`;

            if(props.assignment) {
                if(!seatInfo.label) {
                    className += ` ${classes.assignBlank}`;
                } else {
                    className += ` ${classes.assignSeat}`;
                    
                    if(props.assignment[seatInfo.label]) {
                        className += ` ${classes.assignFilled}`;
                    } else {
                        className += ` ${classes.assignEmpty}`;
                    }
                }
            } else {
                className += ` ${props.selected.has(`${i} ${j}`) ? classes.layoutSelected : classes.layoutUnselected}`;

                if(seatInfo.error) {
                    className += ` ${classes.layoutError}`;
                } else if(!seatInfo.label) {
                    className += ` ${classes.layoutBlank}`;
                } else if(seatInfo.broken) {
                    className += ` ${classes.layoutBroken}`;
                } else if(seatInfo.left) {
                    className += ` ${classes.layoutLeftSeat}`;
                } else {
                    className += ` ${classes.layoutSeat}`;
                }
            }

            row.push(
                <Grid item key={`${seatInfo.label} ${i} ${j}`}>
                    <Box
                      id={`${i},${j}`}
                      className={className}
                      onMouseDown={(event) => props.handleMouseDown(event, i, j)}
                      onMouseUp={(event) => props.handleMouseUp(event, i, j)}
                      onMouseOver={(event) => props.handleMouseOver(i,j)}
                    >
                        {seatInfo.label}
                    </Box>
                </Grid>
            );
        }

        seats2D.push(
            <Grid container item key={i} wrap="nowrap">
                {row}
            </Grid>
        );
    }

    return (
        <Grid container direction="column" wrap="nowrap">
            {seats2D}
        </Grid>
    )
}
