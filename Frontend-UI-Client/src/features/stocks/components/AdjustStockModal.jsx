import React, { useState } from 'react';
import Modal from '@/components/ui/Modal';
import FormInput from '@/components/ui/form/FormInput';
import FormSelect from '@/components/ui/form/FormSelect';

const EVENT_TYPES = [
    { value: 'ingreso_ajuste', label: 'Ingreso por Ajuste (+)' },
    { value: 'egreso_ajuste', label: 'Egreso por Ajuste (-)' },
];

const AdjustStockModal = ({ open, onClose, onSubmit, isLoading }) => {
    const [eventType, setEventType] = useState(EVENT_TYPES[0].value);
    const [quantity, setQuantity] = useState('');
    const [notes, setNotes] = useState('');
    const [error, setError] = useState(null);

    const handleSubmit = (e) => {
        e.preventDefault();
        setError(null);
        const qty = Number(quantity);
        if (!qty || qty === 0) {
            setError('La cantidad debe ser distinta de cero.');
            return;
        }
        if (!notes.trim()) {
            setError('La observación es obligatoria.');
            return;
        }
        onSubmit({ event_type: eventType, quantity_change: qty, notes });
    };

    return (
        <Modal isOpen={open} onClose={onClose} title="Ajustar Stock del Subproducto">
            <form className="flex flex-col gap-4 p-4" onSubmit={handleSubmit}>
                <FormSelect
                    label="Tipo de Ajuste"
                    name="eventType"
                    value={eventType}
                    options={EVENT_TYPES}
                    onChange={(e) => setEventType(e.target.value)}
                />
                <FormInput
                    label="Cantidad"
                    name="quantity"
                    type="number"
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    min={-99999}
                    max={99999}
                    required
                />
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Observación/Justificación</label>
                    <textarea
                        className="w-full border rounded px-3 py-2 text-gray-700 focus:outline-none focus:ring focus:border-blue-300"
                        rows={3}
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        required
                        placeholder="Describe el motivo del ajuste (obligatorio)"
                    />
                </div>
                {error && <div className="text-red-500 text-sm mb-2">{error}</div>}
                <div className="flex justify-end gap-2 mt-2">
                    <button
                        type="button"
                        className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
                        onClick={onClose}
                        disabled={isLoading}
                    >
                        Cancelar
                    </button>
                    <button
                        type="submit"
                        className="bg-primary-500 text-white px-4 py-2 rounded hover:bg-primary-600"
                        disabled={isLoading}
                    >
                        {isLoading ? 'Guardando...' : 'Confirmar Ajuste'}
                    </button>
                </div>
            </form>
        </Modal>
    );
};

export default AdjustStockModal;