import FormGroupInput from "./Inputs/formGroupInput.vue";

import DropDown from "./Dropdown.vue";
import PaperTable from "./PaperTable.vue";
import ActionTable from "./ActionTable.vue";
import Button from "./Button";

import Card from "./Cards/Card.vue";
import ChartCard from "./Cards/ChartCard.vue";
import StatsCard from "./Cards/StatsCard.vue";

import SidebarPlugin from "./SidebarPlugin/index";

let components = {
  FormGroupInput,
  Card,
  ChartCard,
  StatsCard,
  PaperTable,
  ActionTable,
  DropDown,
  SidebarPlugin
};

export default components;

export {
  FormGroupInput,
  Card,
  ChartCard,
  StatsCard,
  PaperTable,
  ActionTable,
  DropDown,
  Button,
  SidebarPlugin
};
