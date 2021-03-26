/* File name: routes.js
 * Author: Queues Team, @nouryehia
 * Description: Defines all the routes to be used by the Frontend.
 */

import React from 'react';
import { Redirect, Route, Switch } from 'react-router-dom';

// Import routes
import Temp from './routes/temp';

const Routes = () => {
    return (
        <Switch>
            <Route path='/' exact component={Temp}>
                <Redirect to="/temp" />
            </Route>
            <Route exact path="/temp" component={Temp} />
        </Switch>
    );
}

export default Routes;