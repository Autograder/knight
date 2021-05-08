import Styles from "../style/SeatingStyle";
import { Grid, Box } from "@material-ui/core";
import React from "react";

export default function SeatLayout(props) {
    const classes = Styles.useStyles();

    let handleMouseDown = props.handleMouseDown !== undefined ? props.handleMouseDown : () => {};
    let handleMouseUp = props.handleMouseUp !== undefined ? props.handleMouseUp : () => {};
    let handleMouseOver = props.handleMouseOver !== undefined ? props.handleMouseOver : () => {};
    let selected = props.selected !== undefined ? props.selected : new Set();

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
                    } else if(seatInfo.broken) {
                        className += ` ${classes.assignBroken}`;
                    } else {
                        className += ` ${classes.assignEmpty}`;
                    }

                    if(seatInfo.left) {
                        className += ` ${classes.assignLeft}`;
                    }
                }
            } else {
                className += ` ${selected.has(`${i} ${j}`) ? classes.layoutSelected : classes.layoutUnselected}`;

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
                      onMouseDown={(event) => handleMouseDown(event, i, j)}
                      onMouseUp={(event) => handleMouseUp(event, i, j)}
                      onMouseOver={(event) => handleMouseOver(i,j)}
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

    if(props.hidden) {
        return null;
    }
    
    return (
        <React.Fragment>
            <div className={classes.frontBanner}>Front</div>
            <Grid container direction="column" wrap="nowrap" alignItems="center" justify="center">
                {seats2D}
            </Grid>
            <div className={classes.frontBanner}>Back</div>
        </React.Fragment>
    )
}
