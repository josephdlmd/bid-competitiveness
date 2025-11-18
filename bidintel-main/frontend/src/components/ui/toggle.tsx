import * as React from "react"
import { cn } from "@/lib/utils"

interface ToggleProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  checked?: boolean
  onCheckedChange?: (checked: boolean) => void
}

const Toggle = React.forwardRef<HTMLInputElement, ToggleProps>(
  ({ className, checked, onCheckedChange, ...props }, ref) => {
    return (
      <label className="relative inline-flex items-center cursor-pointer">
        <input
          type="checkbox"
          ref={ref}
          checked={checked}
          onChange={(e) => onCheckedChange?.(e.target.checked)}
          className="sr-only peer"
          {...props}
        />
        <div className={cn(
          "w-11 h-6 bg-slate-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-slate-400 rounded-full peer",
          "peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px]",
          "after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all",
          "peer-checked:bg-slate-900",
          className
        )} />
      </label>
    )
  }
)
Toggle.displayName = "Toggle"

export { Toggle }
