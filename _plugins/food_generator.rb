require 'json'

module Jekyll
  class FoodPageGenerator < Generator
    safe true
    priority :normal

    def generate(site)
      items = load_json(site, '_rawdata/food.json')
      Jekyll.logger.info "FoodGenerator:", "#{items.size}개 음식 페이지 생성 중..."
      items.each do |f|
        next if f['slug'].to_s.strip.empty?
        site.pages << FoodPage.new(site, f)
      end
      Jekyll.logger.info "FoodGenerator:", "완료 (#{items.size}개)"
    end

    private

    def load_json(site, path)
      file = File.join(site.source, path)
      return [] unless File.exist?(file)
      JSON.parse(File.read(file, encoding: 'utf-8'))
    rescue => e
      Jekyll.logger.warn "FoodGenerator:", "#{path} 로드 실패: #{e.message}"
      []
    end
  end

  class FoodPage < Page
    def initialize(site, f)
      @site = site
      @base = site.source
      @dir  = "food/#{f['slug']}"
      @name = 'index.html'

      self.process(@name)
      self.read_yaml(File.join(@base, '_layouts'), 'food.html')
      self.data.merge!(f)
      self.data['layout']      = 'food'
      self.data['title']       = build_title(f)
      self.data['description'] = build_desc(f)
    end

    private

    def build_title(f)
      kcal = f['energy'].to_s.empty? ? '' : " #{f['energy']}kcal"
      "#{f['foodName']} 칼로리·영양성분#{kcal}"
    end

    def build_desc(f)
      qty = f['baseQty'].to_s.empty? ? '100g' : f['baseQty']
      "#{f['foodName']}(#{f['category']}) #{qty} 기준 칼로리 #{f['energy']}kcal, 탄수화물 #{f['carb']}g, 단백질 #{f['protein']}g, 지방 #{f['fat']}g"[0, 155]
    end
  end
end
