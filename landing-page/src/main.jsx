// import { StrictMode } from 'react'
// import { createRoot } from 'react-dom/client'

import React from 'react';
import { createRoot } from 'react-dom/client';
import { Auth0Provider } from '@auth0/auth0-react';
import './index.css'
import App from './App';

const root = createRoot(document.getElementById('root'));

root.render(
<Auth0Provider
    domain="dev-gv7r58hms8lw2uv0.us.auth0.com"
    clientId="OVLNqZZatCnAANcD6Dsv25lX2W9NOmSZ"
    authorizationParams={{
      redirect_uri: window.location.origin
    }}
  >
    <App />
  </Auth0Provider>,
);