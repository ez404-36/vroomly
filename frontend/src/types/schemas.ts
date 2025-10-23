/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type ID = string | number;
/**
 * Тип ТС
 */
export type VehicleType = 0 | 1;

/**
 * Intended for use as a base class for externally-facing models.
 *
 * Any models that inherit from this class will:
 * * accept fields using snake_case or camelCase keys
 * * use camelCase keys in the generated OpenAPI spec
 * * have orm_mode on by default
 *     * Because of this, FastAPI will automatically attempt to parse returned orm instances into the model
 */
export interface APIModel {}
export interface CarInfoByVINSchema {
  success: boolean;
  status: number;
  data: CarInfoByVinDataSchema;
}
export interface CarInfoByVinDataSchema {
  model: string;
  year: number;
  frame: string | null;
  vin: string;
  carplate: string;
  color: string;
  type: string;
  volume: number;
  power: number;
  frame_id: number;
  vehicle_type: string;
}
export interface ChoiceFieldSchema {
  id: ID;
  name: string;
}
export interface ChoiceFieldWithParentSchema {
  id: ID;
  name: string;
  parent: ChoiceFieldSchema;
}
export interface CountryDetailSchema {
  id: string;
  name: string;
  shortName: string | null;
}
/**
 * Модель текущего пользователя, доступная в API-запросах
 */
export interface CurrentUser {
  id: string;
  login: string;
  email: string;
  name: string | null;
  surname: string | null;
  birthDate: string | null;
}
/**
 * Модель данных, в которой запрещено изменять поля
 */
export interface FrozenModelType {}
export interface GuessCommonCarInfoSchema {
  brand: ChoiceFieldSchema1;
  model: ChoiceFieldSchema2;
  /**
   * Поколение
   */
  generation: ChoiceFieldSchema[];
  /**
   * Комплектация
   */
  configuration: ChoiceFieldWithParentSchema[];
}
/**
 * Бренд
 */
export interface ChoiceFieldSchema1 {
  id: ID;
  name: string;
}
/**
 * Модель
 */
export interface ChoiceFieldSchema2 {
  id: ID;
  name: string;
}
/**
 * Определенный переводчиком язык
 */
export interface LibreTranslateDetectedLanguage {
  confidence: number;
  language: string;
}
/**
 * Модель ответа LibreTranslate
 */
export interface LibreTranslateResponse {
  translatedText: string;
  alternatives: string[];
  detectedLanguage?: LibreTranslateDetectedLanguage | null;
}
export interface RegistrationDataForm {
  login: string;
  email: string;
  password: string;
  confirm_password: string;
}
export interface Token {
  access_token: string;
  token_type: string;
}
export interface TokenData {
  user_id: string | null;
}
export interface VehicleBrandDetailSchema {
  id: string;
  countryId: string;
  code: string;
  name: string;
  originalName: string | null;
}
export interface VehicleBrandFilterParams {
  /**
   * Сортировка
   */
  ordering?: 'country_id' | 'code';
  /**
   * Поиск (по названию/коду)
   */
  search?: string;
  /**
   * Фильтрация по коду страны
   */
  country?: string;
}
export interface VehicleDetailSchema {
  id: string;
  vehicleType: VehicleType;
  productionYear: number;
  color: string | null;
}
export interface VehicleSeriesDetailSchema {
  id: string;
  name: string;
  brand: VehicleBrandDetailSchema;
}
export interface VehicleSeriesFilterParams {
  /**
   * ID бренда
   */
  brand: string;
  /**
   * Поиск по названию модели
   */
  search?: string;
}
export interface VehicleSeriesListSchema {
  id: string;
  name: string;
  brandId: string;
}
