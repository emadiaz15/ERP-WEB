// src/components/common/Table.jsx
import React from 'react';
import TableHeader from './TableHeader';
import TableRow from './TableRow';

const Table = ({ headers, rows, footer }) => (
  <div className="overflow-x-auto">
    <div className="max-h-[400px] overflow-y-auto"> {/* altura y scroll vertical */}
      <table className="w-full text-sm text-left text-text-primary">
        <thead className="sticky top-0 z-10">
          <TableHeader headers={headers} />
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <TableRow key={index} rowData={row} isEven={index % 2 === 0} />
          ))}
          {/* Sentinel row para infinite scroll */}
          {footer}
        </tbody>
      </table>
    </div>
  </div>
);

export default Table;
