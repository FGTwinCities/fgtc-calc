import htmx from "htmx.org";

import { registerHtmxExtension } from "litestar-vite-plugin/helpers";

import './style.css';

window.htmx = htmx;

registerHtmxExtension();
htmx.process(document.body);
