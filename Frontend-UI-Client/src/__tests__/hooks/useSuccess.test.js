import { renderHook } from '@testing-library/react';
import useSuccess from '../../hooks/useSuccess';

describe('useSuccess', () => {
  it('puede llamarse sin errores', () => {
    renderHook(() => useSuccess());
  });
});
