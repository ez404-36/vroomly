import { uiConfig, type UIProvider } from './config/provider';
import { MantineButton } from './components/Button/MantineButton';
import type { ButtonProps } from './components/Button/types';
import { MantineTextInput } from './components/TextInput/MantineTextInput';
import type { TextInputProps } from './components/TextInput/types';
import { MantinePasswordInput } from './components/PasswordInput/MantinePasswordInput';
import type { PasswordInputProps } from './components/PasswordInput/types';
import { MantineNumberInput } from './components/NumberInput/MantineNumberInput';
import type { NumberInputProps } from './components/NumberInput/types';
import { MantineSelect } from './components/Select/MantineSelect';
import type { SelectProps } from './components/Select/types';
import { MantineSwitch } from './components/Switch/MantineSwitch';
import type { SwitchProps } from './components/Switch/types';
import { MantineContainer } from './components/Container/MantineContainer';
import type { ContainerProps } from './components/Container/types';
import { MantinePaper } from './components/Paper/MantinePaper';
import type { PaperProps } from './components/Paper/types';
import { MantineStack } from './components/Stack/MantineStack';
import type { StackProps } from './components/Stack/types';
import { MantineFlex } from './components/Flex/MantineFlex';
import type { FlexProps } from './components/Flex/types';
import { MantineText } from './components/Text/MantineText';
import type { TextProps } from './components/Text/types';
import { MantineTitle } from './components/Title/MantineTitle';
import type { TitleProps } from './components/Title/types';
import { MantineActionIcon } from './components/ActionIcon/MantineActionIcon';
import type { ActionIconProps } from './components/ActionIcon/types';
import { MantineTooltip } from './components/Tooltip/MantineTooltip';
import type { TooltipProps } from './components/Tooltip/types';
import { MantineIndicator } from './components/Indicator/MantineIndicator';
import type { IndicatorProps } from './components/Indicator/types';
import { MantineDatePickerInput } from './components/DatePickerInput/MantineDatePickerInput';
import type { DatePickerInputProps } from './components/DatePickerInput/types';

type ComponentName = 'Button' | 'TextInput' | 'PasswordInput' | 'NumberInput' | 'Select' | 'Switch' | 'Container' | 'Paper' | 'Stack' | 'Flex' | 'Text' | 'Title' | 'ActionIcon' | 'Tooltip' | 'Indicator' | 'DatePickerInput';

const componentMap: Record<UIProvider, Partial<Record<ComponentName, React.ComponentType<any>>>> = {
  mantine: {
    Button: MantineButton,
    TextInput: MantineTextInput,
    PasswordInput: MantinePasswordInput,
    NumberInput: MantineNumberInput,
    Select: MantineSelect,
    Switch: MantineSwitch,
    Container: MantineContainer,
    Paper: MantinePaper,
    Stack: MantineStack,
    Flex: MantineFlex,
    Text: MantineText,
    Title: MantineTitle,
    ActionIcon: MantineActionIcon,
    Tooltip: MantineTooltip,
    Indicator: MantineIndicator,
    DatePickerInput: MantineDatePickerInput,
  },
  mui: {},
  chakra: {},
  shadcn: {},
};

const cache = new Map<string, React.ComponentType<any>>();

export function createComponentGetter() {
  return function getComponent(name: ComponentName): React.ComponentType<any> {
    const cacheKey = `${name}-${uiConfig.provider}`;

    if (cache.has(cacheKey)) {
      return cache.get(cacheKey)!;
    }

    const provider = uiConfig.provider;
    const Component = componentMap[provider]?.[name] || componentMap.mantine[name];

    if (!Component) {
      throw new Error(`[UI Factory] Component ${name} not found for provider ${provider}`);
    }

    cache.set(cacheKey, Component);
    return Component;
  };
}

export const getComponent = createComponentGetter();

export function Button(props: ButtonProps) {
  const Component = getComponent('Button') as React.ComponentType<ButtonProps>;
  return <Component {...props} />;
}

export function TextInput(props: TextInputProps) {
  const Component = getComponent('TextInput') as React.ComponentType<TextInputProps>;
  return <Component {...props} />;
}

export function PasswordInput(props: PasswordInputProps) {
  const Component = getComponent('PasswordInput') as React.ComponentType<PasswordInputProps>;
  return <Component {...props} />;
}

export function NumberInput(props: NumberInputProps) {
  const Component = getComponent('NumberInput') as React.ComponentType<NumberInputProps>;
  return <Component {...props} />;
}

export function Select(props: SelectProps) {
  const Component = getComponent('Select') as React.ComponentType<SelectProps>;
  return <Component {...props} />;
}

export function Switch(props: SwitchProps) {
  const Component = getComponent('Switch') as React.ComponentType<SwitchProps>;
  return <Component {...props} />;
}

export function Container(props: ContainerProps) {
  const Component = getComponent('Container') as React.ComponentType<ContainerProps>;
  return <Component {...props} />;
}

export function Paper(props: PaperProps) {
  const Component = getComponent('Paper') as React.ComponentType<PaperProps>;
  return <Component {...props} />;
}

export function Stack(props: StackProps) {
  const Component = getComponent('Stack') as React.ComponentType<StackProps>;
  return <Component {...props} />;
}

export function Flex(props: FlexProps) {
  const Component = getComponent('Flex') as React.ComponentType<FlexProps>;
  return <Component {...props} />;
}

export function Text(props: TextProps) {
  const Component = getComponent('Text') as React.ComponentType<TextProps>;
  return <Component {...props} />;
}

export function Title(props: TitleProps) {
  const Component = getComponent('Title') as React.ComponentType<TitleProps>;
  return <Component {...props} />;
}

export function ActionIcon(props: ActionIconProps) {
  const Component = getComponent('ActionIcon') as React.ComponentType<ActionIconProps>;
  return <Component {...props} />;
}

export function Tooltip(props: TooltipProps) {
  const Component = getComponent('Tooltip') as React.ComponentType<TooltipProps>;
  return <Component {...props} />;
}

export function Indicator(props: IndicatorProps) {
  const Component = getComponent('Indicator') as React.ComponentType<IndicatorProps>;
  return <Component {...props} />;
}

export function DatePickerInput(props: DatePickerInputProps) {
  const Component = getComponent('DatePickerInput') as React.ComponentType<DatePickerInputProps>;
  return <Component {...props} />;
}
