export function AppsView() {
  return <div>Apps View - To be implemented</div>;
}

export function FieldsView() {
  return <div>Fields View - To be implemented</div>;
}

export function DataView() {
  return <div>Data View - To be implemented</div>;
}

export default function Modal({ children, onClose }: { children: React.ReactNode; onClose: () => void }) {
  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 50,
    }} onClick={onClose}>
      <div style={{
        background: 'white',
        padding: 24,
        borderRadius: 8,
        maxWidth: 400,
        width: '90%',
      }} onClick={e => e.stopPropagation()}>
        {children}
      </div>
    </div>
  );
}