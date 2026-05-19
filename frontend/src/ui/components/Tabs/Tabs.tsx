import React from 'react';
import * as TabsPrimitive from '@radix-ui/react-tabs';
import { tabTriggerClass, tabListClass } from './Tabs.styles';

export interface TabItem {
  value: string;
  label: string;
}

export interface TabsProps {
  value: string;
  onValueChange: (value: string) => void;
  tabs: TabItem[];
  children?: React.ReactNode;
  className?: string;
}

export const Tabs = ({
  value,
  onValueChange,
  tabs,
  children,
  className,
}: TabsProps) => {
  return (
    <TabsPrimitive.Root
      value={value}
      onValueChange={onValueChange}
      className={className}
    >
      <TabsPrimitive.List className={tabListClass}>
        {tabs.map((tab) => (
          <TabsPrimitive.Trigger
            key={tab.value}
            value={tab.value}
            className={tabTriggerClass}
            data-testid={`tab-${tab.value}`}
          >
            {tab.label}
          </TabsPrimitive.Trigger>
        ))}
      </TabsPrimitive.List>
      {children}
    </TabsPrimitive.Root>
  );
};

export interface TabContentProps {
  value: string;
  children: React.ReactNode;
  className?: string;
}

export const TabContent = ({
  value,
  children,
  className,
}: TabContentProps) => {
  return (
    <TabsPrimitive.Content value={value} className={className}>
      {children}
    </TabsPrimitive.Content>
  );
};