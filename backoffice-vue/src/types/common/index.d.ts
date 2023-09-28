export type YearMonth = string;
export type ProductData = {
  last_day: number;
  u: number;
  cx: number;
  cx9: number;
};

export type ProductStock = {
  id?: number;
  company: string;
  bo?: string;
  description: string;
  min_ord_qty: number;
  stock: number;
  min_stock: number;
  min_reserved: number;
  min_ordered: number;
  family: string;
  planning?: string;
  ord_mult: number;
  article: string;
  lead_time?: number;
  history: {
    [key: YearMonth]: ProductData;
  };
  forecast: {
    [key: YearMonth]: ProductData;
  };
};

export type Product = {
  id?: string;
  familia?: string;
  artigo: string;
  empresa?: string;
  brandOwner?: string;
  descricao?: string;
  mirOrdQty: number;
  stock: number;
  planing?: number;
  ordrMult: number;
  leadTime?: number;
  minStock: number;
  mediaTrimestral?: number;
  tendenciaTrimestral?: number;
  mediaAnual?: number;
  tendenciaAnual?: number;
  tendenciaPonderada?: number;
  tendenciaAnualBase?: number;
  historicoDoVendas?: [];
  previsaoDeVendas?: [];
};

export type UpdateRequest = {
  product: Product;
  user: string;
  requestDate: string;
  quantity: number;
  quantityNew: number;
  entity: string;
};

export type DataTableHeader = {
  title: string;
  field: string;
  align?: "start" | "center" | "end";
  sortable?: boolean;
  filterable?: boolean;
  groupable?: boolean;
  divider?: boolean;
  class?: string | string[];
  cellClass?: string | string[];
  width?: string | number;
  filter?: (value: any, search: string, item: any) => boolean;
  sort?: (a: any, b: any) => number;
};
