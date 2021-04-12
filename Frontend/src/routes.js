/* File name: routes.js
 * Author: Queues Team, @nouryehia
 * Description: Defines all the routes to be used by the Frontend.
 */

import React from 'react';
import { Redirect, Route, Switch } from 'react-router-dom';
import Seating from './routes/Seating';

// Import routes
import Temp from './routes/temp';

const Routes = () => {
    return (
        <Switch>
            <Route path='/' exact component={Temp}>
                <Redirect to="/temp" />
            </Route>
            <Route exact path="/temp" component={Temp} />
            <Route exact path="/seating" component={Seating} />
        </Switch>
    );
}

export default Routes;