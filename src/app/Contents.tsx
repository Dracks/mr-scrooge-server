import * as React from 'react';
import Loadable from 'react-loadable';
import { Route, Switch } from 'react-router-dom';

import { CenteredLoading } from '../components/Loading';


const GraphReportPage = Loadable({
    loader: () => import("./Pages/GraphReportPage"),
    loading: CenteredLoading
});

const ImportPage = Loadable({
    loader: ()=> import('./Pages/ImportPage'),
    loading: CenteredLoading,
});

const RawDataPage = Loadable({
    loader: ()=> import('./Pages/RawDataPage'),
    loading: CenteredLoading,
});

const TagPage = Loadable({
    loader: ()=> import('./Pages/TagPage'),
    loading: CenteredLoading,
});

const Contents = () => {
    return (
      <div>
        <Switch>
            <Route
                path="/"
                exact={true}
                component={GraphReportPage} />
            <Route
                path="/raw-data"
                component={RawDataPage}/>
            <Route
                path="/tag"
                component={TagPage} />
            <Route
                path="/import"
                component={ImportPage} />
        </Switch>
      </div>
    );
}

export default Contents
