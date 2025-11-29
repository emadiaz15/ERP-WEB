require('@testing-library/jest-dom');

// Mock global ResizeObserver para headlessui/react y otros UI libs
global.ResizeObserver = class {
	observe() {}
	unobserve() {}
	disconnect() {}
};
// Mock global para canvas en jsdom
Object.defineProperty(HTMLCanvasElement.prototype, 'getContext', {
	value: () => ({
		clearRect: jest.fn(),
		fillRect: jest.fn(),
		beginPath: jest.fn(),
		moveTo: jest.fn(),
		lineTo: jest.fn(),
		arc: jest.fn(),
		fill: jest.fn(),
		stroke: jest.fn(),
		closePath: jest.fn(),
		fillStyle: '',
		strokeStyle: '',
	}),
});
